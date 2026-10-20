"""Require a content-specific attestation before displaying a reviewed label.

This verifies the recorded evidence, not the identity or expertise of a reviewer.
Drafts remain publishable with their explicit pending-review label.
"""
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent


def content_digest(record):
    payload = {key: value for key, value in record.items()
               if key not in ('id', 'reviewer_status')}
    return sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                             separators=(',', ':')).encode()).hexdigest()


def validate_review(record, identity, attestations=None):
    review = record.get('reviewer_status', {})
    if review.get('status') not in ('reviewed', 'approved'):
        return
    if attestations is None:
        attestations = json.loads((ROOT/'content/reviews.json').read_text())
    proof = attestations.get(identity, {})
    if (proof.get('sha256') != content_digest(record)
            or proof.get('reviewer') != review.get('reviewer')
            or proof.get('reviewed_at') != review.get('reviewed_at')
            or not proof.get('review_notes', '').strip()
            or not review.get('reviewer', '').strip()
            or 'pending' in review.get('reviewer', '').lower()):
        raise ValueError('Reviewed content needs a matching content-specific attestation: '+identity)
