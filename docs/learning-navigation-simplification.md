# One learning journey — 22 October 2026

The maintainer requested removal of the Capstones, Engineering courses, System
visualizers, Question bank and Topic coverage pages when they duplicate chapter
learning. The duplication was real for the interview bank and coverage index.
Visualizers were already embedded in four chapters. The course and capstone
indexes also linked unique instructional material, so deleting all their targets
would have removed useful examples, starter projects and assessment rubrics.

The change removes all five aggregate HTML pages and their navigation links,
plus the duplicate per-topic bank HTML renderer, filter controls and redirect
logic. Answers and search results use the existing chapter question anchors.
Bounded question JSON and lazy search shards remain because search and contributor
quality reports consume them; they do not create a second reader.

All 40 worked course units remain available as contextual chapter extensions.
Eighteen previously had no main-chapter placement; each now has one. The curriculum
manifest is the single source of that mapping instead of divergent chapter JSON
copies. Unit navigation returns to its owning chapter. The four original project
starters/rubrics are linked from their relevant chapter and the final portfolio
chapter. All four interactive state simulations and no-JS transcripts remain in
their existing chapters.

This intentionally retires the duplicate index/bank URLs. Chapter URLs, stable
question IDs, unit URLs, notes/bookmarks and exported study records remain intact.
Saved focus mode no longer hides navigation on a later visit: focus is page-local
and opt-in. Editorial banners are removed from rendered learning pages while
source review records and validation retain their evidence.

Validation uses the existing full build/link/source checks and browser suites.
The scale checks now verify 1,200 direct chapter anchors in JS and no-JS browsers,
bounded data/search shards and absence of duplicate answer pages, rather than
asserting the retired pagination UI. Navigation checks require every unit,
project and inline simulation to remain reachable. Accessibility still checks
those actual templates and simulations from their chapter entry points.

Recovery is a source revert of this PR; no storage schema or learner data is
migrated. The retained source records can rebuild every instructional artifact.
