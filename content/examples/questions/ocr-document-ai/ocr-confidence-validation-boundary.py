#!/usr/bin/env python3
"""
OCR Confidence Validation Boundary Harness
Demonstrates why high OCR confidence scores fail to guarantee business correctness,
and validates multi-layer deterministic field validation and human-in-the-loop gating.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class OCRExtractedToken:
    text: str
    confidence: float  # 0.0 to 1.0
    bounding_box: Tuple[int, int, int, int]  # (left, top, width, height)


@dataclass
class ExtractedPolicyRecord:
    doc_id: str
    page_number: int
    raw_ocr_text: str
    refund_period_days: int
    mean_token_confidence: float
    validation_passed: bool
    status: str


class DocumentExtractionEngine:
    """Simulates an OCR and Document AI extraction pipeline."""

    @staticmethod
    def parse_scan_with_ocr(simulated_misread: bool = False) -> List[OCRExtractedToken]:
        if simulated_misread:
            # Common OCR failure: '14' misread as '74' with falsely high confidence
            return [
                OCRExtractedToken("Returns", 0.98, (10, 20, 50, 15)),
                OCRExtractedToken("must", 0.99, (65, 20, 35, 15)),
                OCRExtractedToken("be", 0.97, (105, 20, 20, 15)),
                OCRExtractedToken("completed", 0.95, (130, 20, 70, 15)),
                OCRExtractedToken("within", 0.96, (205, 20, 45, 15)),
                OCRExtractedToken("74", 0.94, (255, 20, 25, 15)),  # Misread!
                OCRExtractedToken("days.", 0.98, (285, 20, 40, 15)),
            ]
        else:
            return [
                OCRExtractedToken("Returns", 0.98, (10, 20, 50, 15)),
                OCRExtractedToken("must", 0.99, (65, 20, 35, 15)),
                OCRExtractedToken("be", 0.97, (105, 20, 20, 15)),
                OCRExtractedToken("completed", 0.95, (130, 20, 70, 15)),
                OCRExtractedToken("within", 0.96, (205, 20, 45, 15)),
                OCRExtractedToken("14", 0.99, (255, 20, 25, 15)),
                OCRExtractedToken("days.", 0.98, (285, 20, 40, 15)),
            ]

    @staticmethod
    def extract_and_validate(tokens: List[OCRExtractedToken]) -> ExtractedPolicyRecord:
        full_text = " ".join(t.text for t in tokens)
        mean_conf = sum(t.confidence for t in tokens) / len(tokens)

        # Extract numerical days
        days = 0
        for t in tokens:
            if t.text.isdigit():
                days = int(t.text)
                break

        # Business Validation Boundary:
        # Standard retail refund windows are strictly 7, 14, 30, 60, or 90 days.
        # Unrecognized values like 74 trigger deterministic validation rejection.
        valid_standard_windows = {7, 14, 30, 60, 90}
        is_valid = days in valid_standard_windows

        status = "APPROVED_FOR_INDEXING" if is_valid else "QUARANTINED_FOR_HUMAN_REVIEW"

        return ExtractedPolicyRecord(
            doc_id="policy_return_scan_01",
            page_number=1,
            raw_ocr_text=full_text,
            refund_period_days=days,
            mean_token_confidence=mean_conf,
            validation_passed=is_valid,
            status=status
        )


def main() -> None:
    # --------------------------------------------------------------------------
    # Scenario: High Confidence Misrecognition Trap
    # Physical document states 14 days. OCR misreads 14 as 74 with 94% confidence.
    # --------------------------------------------------------------------------
    misread_tokens = DocumentExtractionEngine.parse_scan_with_ocr(simulated_misread=True)
    record = DocumentExtractionEngine.extract_and_validate(misread_tokens)

    # Invariant 1: High OCR extraction confidence does NOT imply business correctness
    assert record.mean_token_confidence > 0.95
    assert record.refund_period_days == 74  # Extracted value is factually wrong!

    # Invariant 2: Downstream RAG generation follows the text faithfully, repeating the defect
    # A naive RAG generator citing this text would claim 74 days with 100% faithfulness score!
    simulated_rag_answer = f"According to the policy, returns must be completed within {record.refund_period_days} days [policy_return_scan_01]."
    assert "74 days" in simulated_rag_answer

    # Invariant 3: Deterministic Field Validation stops automated indexing
    assert record.validation_passed is False
    assert record.status == "QUARANTINED_FOR_HUMAN_REVIEW"

    # --------------------------------------------------------------------------
    # Case 2: Clean Extraction Passes Validation
    # --------------------------------------------------------------------------
    clean_tokens = DocumentExtractionEngine.parse_scan_with_ocr(simulated_misread=False)
    clean_record = DocumentExtractionEngine.extract_and_validate(clean_tokens)

    assert clean_record.refund_period_days == 14
    assert clean_record.validation_passed is True
    assert clean_record.status == "APPROVED_FOR_INDEXING"

    print("All OCR confidence validation boundary invariants verified successfully.")


if __name__ == "__main__":
    main()
