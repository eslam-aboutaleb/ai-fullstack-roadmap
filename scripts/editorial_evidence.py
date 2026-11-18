"""Editorial review, primary-source citation, and evidence inventory checks."""
from roadmap.config import CONTENT, ROOT
from roadmap.editorial import (
    ADOPTION_ID,
    PLACEHOLDERS,
    acceptable_url,
    evidence_report as _evidence_report,
    inspect_new_question,
    validate_new_records,
)


def evidence_report(chapters):
    """Aggregate factual source inventory across chapters and courses."""
    return _evidence_report(chapters, content_dir=CONTENT)
