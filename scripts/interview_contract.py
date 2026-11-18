"""Authoring contract checks for post-baseline interview topics and chapter framing."""
from roadmap.editorial import (
    BASELINE_ID,
    MIN_DEEP_ANSWER,
    _good_text,
    check_interview_contract as check,
    inspect_interview_contract as inspect,
)

if __name__ == '__main__':
    import json
    from course_data import load

    print(json.dumps(check(load()), indent=2))
