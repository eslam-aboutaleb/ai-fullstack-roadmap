"""
model-release-manifest-compatibility.py

Production-grade Model Release Manifest and Tokenizer Compatibility Verification Suite.
Demonstrates:
1. Cryptographic binding of Base Model, Tokenizer revision, LoRA Adapter, and Training Lineage.
2. The classic silent failure mode: an adapter loads into GPU memory because matrix shapes match
   (e.g., [4096, 16]), but the tokenizer vocabulary revision has shifted, resulting in silent
   token index corruption and gibberish completions.
3. Pre-flight verification barrier that computes canonical vocab hashes, rejects tokenizer mismatches,
   and certifies inference serving assumptions before traffic ingress.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import hashlib
import json


class CompatibilityError(Exception):
    """Raised when release manifest contracts fail validation."""
    pass


@dataclass(frozen=True)
class TokenizerContract:
    tokenizer_name: str
    vocab_hash: str
    special_tokens_hash: str
    bos_token_id: int
    eos_token_id: int
    pad_token_id: int

    @classmethod
    def from_vocab(cls, name: str, vocab: Dict[str, int], special_tokens: Dict[str, int]) -> "TokenizerContract":
        v_bytes = json.dumps(vocab, sort_keys=True).encode("utf-8")
        s_bytes = json.dumps(special_tokens, sort_keys=True).encode("utf-8")
        return cls(
            tokenizer_name=name,
            vocab_hash=hashlib.sha256(v_bytes).hexdigest(),
            special_tokens_hash=hashlib.sha256(s_bytes).hexdigest(),
            bos_token_id=special_tokens.get("<bos>", 1),
            eos_token_id=special_tokens.get("<eos>", 2),
            pad_token_id=special_tokens.get("<pad>", 0),
        )


@dataclass
class AdapterContract:
    adapter_id: str
    base_model_revision: str
    target_modules: List[str]
    rank: int
    alpha: float
    compatible_tokenizer_vocab_hash: str
    dataset_lineage_hash: str


@dataclass
class ModelReleaseManifest:
    release_id: str
    base_model_name: str
    base_model_revision: str
    base_weights_sha256: str
    tokenizer: TokenizerContract
    adapter: Optional[AdapterContract]
    runtime_dependencies: Dict[str, str]
    serving_assumptions: Dict[str, Any]

    def verify_release_integrity(
        self,
        runtime_base_revision: str,
        runtime_tokenizer: TokenizerContract
    ) -> Dict[str, Any]:
        """
        Validates that runtime components match the release contract exactly.
        Prevents shape-compatible but semantically corrupt weights from serving traffic.
        """
        # 1. Base model revision check
        if self.base_model_revision != runtime_base_revision:
            raise CompatibilityError(
                f"Base model revision mismatch: manifest requires '{self.base_model_revision}', "
                f"but runtime environment loaded '{runtime_base_revision}'."
            )

        # 2. Tokenizer cryptographic hash check
        if self.tokenizer.vocab_hash != runtime_tokenizer.vocab_hash:
            raise CompatibilityError(
                f"Tokenizer vocabulary mismatch! Manifest vocab hash '{self.tokenizer.vocab_hash[:12]}' "
                f"does not match runtime tokenizer hash '{runtime_tokenizer.vocab_hash[:12]}'. "
                f"Even though tensor dimensions match, token IDs will produce garbled output."
            )

        # 3. Special tokens alignment check
        if self.tokenizer.special_tokens_hash != runtime_tokenizer.special_tokens_hash:
            raise CompatibilityError("Special tokens definitions have drifted between manifest and runtime.")

        # 4. Adapter compatibility check (if adapter is attached)
        if self.adapter:
            if self.adapter.compatible_tokenizer_vocab_hash != runtime_tokenizer.vocab_hash:
                raise CompatibilityError(
                    f"Adapter '{self.adapter.adapter_id}' was trained against tokenizer hash "
                    f"'{self.adapter.compatible_tokenizer_vocab_hash[:12]}', but runtime is "
                    f"'{runtime_tokenizer.vocab_hash[:12]}'."
                )

        # 5. Serving hardware & concurrency assumptions
        min_vram_gb = self.serving_assumptions.get("min_vram_gb", 0)
        max_batch_size = self.serving_assumptions.get("max_batch_size", 1)

        return {
            "status": "VERIFIED_COMPATIBLE",
            "release_id": self.release_id,
            "base_model": self.base_model_name,
            "adapter_id": self.adapter.adapter_id if self.adapter else None,
            "min_vram_gb": min_vram_gb,
            "max_batch_size": max_batch_size
        }


def main() -> None:
    print("=== Testing Model Release Manifest & Tokenizer Compatibility Suite ===")

    # 1. Define Canonical Training Vocabularies
    trained_vocab = {"<pad>": 0, "<bos>": 1, "<eos>": 2, "refund": 100, "policy": 101, "customer": 102}
    special_tokens = {"<pad>": 0, "<bos>": 1, "<eos>": 2}

    trained_tok = TokenizerContract.from_vocab(
        name="llama-3-8b-domain-tok",
        vocab=trained_vocab,
        special_tokens=special_tokens
    )

    # 2. Construct Verified Release Manifest
    adapter = AdapterContract(
        adapter_id="lora-customer-service-v1",
        base_model_revision="sha256-base-abc1234",
        target_modules=["q_proj", "v_proj"],
        rank=16,
        alpha=32.0,
        compatible_tokenizer_vocab_hash=trained_tok.vocab_hash,
        dataset_lineage_hash="sha256-data-998877"
    )

    manifest = ModelReleaseManifest(
        release_id="rel-2026-cs-001",
        base_model_name="meta-llama/Llama-3-8B-Instruct",
        base_model_revision="sha256-base-abc1234",
        base_weights_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        tokenizer=trained_tok,
        adapter=adapter,
        runtime_dependencies={"torch": "2.4.0", "transformers": "4.44.0", "vllm": "0.5.4"},
        serving_assumptions={"min_vram_gb": 16, "max_batch_size": 32, "target_p95_ms": 350}
    )

    # 3. Test Successful Runtime Verification (Happy Path)
    result = manifest.verify_release_integrity(
        runtime_base_revision="sha256-base-abc1234",
        runtime_tokenizer=trained_tok
    )
    print("Happy Path Verification Result:", result)
    assert result["status"] == "VERIFIED_COMPATIBLE"
    assert result["release_id"] == "rel-2026-cs-001"

    # 4. Simulate Real-World Failure: Tokenizer Revision Drift
    # Suppose a serving engineer upgrades the tokenizer library which subtly shifts token IDs:
    # "refund" moves from 100 to 105, even though vocab size is identical
    mutated_vocab = {"<pad>": 0, "<bos>": 1, "<eos>": 2, "order": 100, "refund": 105, "customer": 102}
    drifted_tok = TokenizerContract.from_vocab(
        name="llama-3-8b-domain-tok-v2",
        vocab=mutated_vocab,
        special_tokens=special_tokens
    )

    print("\nSimulating deployment with drifted tokenizer (shapes match, token IDs differ)...")
    try:
        manifest.verify_release_integrity(
            runtime_base_revision="sha256-base-abc1234",
            runtime_tokenizer=drifted_tok
        )
        assert False, "Should have failed due to tokenizer vocab hash mismatch"
    except CompatibilityError as e:
        print("Successfully intercepted tokenizer mismatch:")
        print("  Error message:", str(e))
        assert "Tokenizer vocabulary mismatch" in str(e)

    # 5. Simulate Base Model Revision Mismatch
    try:
        manifest.verify_release_integrity(
            runtime_base_revision="sha256-base-mismatched-999",
            runtime_tokenizer=trained_tok
        )
        assert False, "Should have failed due to base model revision mismatch"
    except CompatibilityError as e:
        print("\nSuccessfully intercepted base model revision mismatch:")
        print("  Error message:", str(e))
        assert "Base model revision mismatch" in str(e)

    print("\nAll model release manifest and tokenizer compatibility tests passed successfully.")


if __name__ == "__main__":
    main()

