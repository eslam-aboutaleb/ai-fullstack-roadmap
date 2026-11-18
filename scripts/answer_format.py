"""Compatibility facade delegating prose formatting to roadmap.prose."""
from roadmap.prose import (
    AnswerWriter,
    VISUALS,
    answer_diagram,
    blocks,
    inline,
    normalize,
    prose,
    validate_diagrams,
)

__all__ = [
    'AnswerWriter',
    'VISUALS',
    'answer_diagram',
    'blocks',
    'inline',
    'normalize',
    'prose',
    'validate_diagrams',
]
