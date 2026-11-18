"""Load topic-organized inline question code examples and verify coverage."""
from roadmap.examples import (
    EXTENSIONS,
    LANGUAGES,
    QUESTION_EXAMPLES_DIR as DIRECTORY,
    load_question_examples as _load_question_examples,
)


def load_question_examples(chapters):
    """Load and validate question code catalogs against active DIRECTORY."""
    return _load_question_examples(chapters, directory=DIRECTORY)
