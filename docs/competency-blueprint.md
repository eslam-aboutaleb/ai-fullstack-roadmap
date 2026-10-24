# Curriculum competency blueprint — implementation increment (#11)

The generated `competency-blueprint.html` and
`questions/competency-blueprint.json` are public and static. The JSON links:
- every chapter to prerequisite chapters, stated competency, effort and required artifacts;
- every foundation lesson and deeper interview question to its stable study ID;
- associated browser assessments and coding labs by study ID;
- structured companion units, learning outcomes, practice labs and their prerequisites;
- 12 advanced workstreams (#38–#49) with motivation, outcomes, an introductory case,
  suggested interview questions, local exercises, diagrams and assessments.

Existing chapter material counts as **introduced**, and authored tests/exercises
are available for **practice**. Neither makes the learner independently proficient
or certifies the answers; independent review is currently pending.

## Updating the planned tracks

Edit `content/shared/competency-plan.json` to add concrete, unique and
prerequisite-mapped future modules. Do not change `status` to
`independently-reviewed` without recorded review evidence. Extend each workstream
from its existing prerequisite chapters; avoid cloning an unrelated shallow topic
page. Content should follow the existing introduction → guided questions → deep
interview Q&A → worked code/diagrams → independent practice pattern.

`scripts/learning_blueprint.py` validates the plan during curriculum checks.
The static build emits the readable and JSON versions; `tests/check_learning_blueprint.py`
compares the published artifact to source and tests impossible approval, dangling
chapters, missing interview questions and question-count mismatches.

### Still outstanding

This is an accurate machine-readable *foundation* for completing the exhaustive
full-stack curriculum, not 100% syllabus authoring. The planned modules need
full interview answers, examples, accessibility-reviewed figures, learner tests,
real environment evidence and independent technical review. External SDK/GPU
work cannot be marked completed on the strength of a link or a fictional result.
