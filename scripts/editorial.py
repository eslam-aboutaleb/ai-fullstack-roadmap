"""Require a content-specific SHA-256 attestation before displaying a reviewed label."""
from roadmap.config import CONTENT, ROOT
from roadmap.editorial import content_digest, validate_review as _validate_review


def validate_review(record, identity, attestations=None):
    """Validate review attestation against content/reviews.json."""
    return _validate_review(record, identity, attestations=attestations, content_dir=CONTENT)
