# Shared CI inheritance

The Pages workflow calls reusable workflows from
[eslam-aboutaleb/ci-workflows](https://github.com/eslam-aboutaleb/ci-workflows)
at reviewed commit `f989c2d0742cdab6cdef8437685d128b28904abc`.

| Inherited workflow | Contract in this repository |
| --- | --- |
| `project-check.yml` | Python 3.11 and Node 22; `make ci-install` installs the verified optional Python browser runtime; `make ci-quality` runs the static build, content/source/schema/link checks, JavaScript rules and local standard-library pilots. |
| `workflow-lint.yml` | Runs Actionlint against this repository's Actions definitions. |
| `security.yml` | CodeQL `security-extended` analysis for Python, JavaScript and Actions; pull-request dependency review rejects newly introduced high/critical dependency risks. |

Calls use immutable commit references and pass no secrets. The security caller
grants only the scopes declared by that workflow; build/test calls retain
`contents: read`. Update the three pins together after reviewing upstream changes.

Repository-specific browser, accessibility, scale, temporary PostgreSQL and
NumPy/PyTorch checks remain in the Pages workflow. The final **Quality gate** runs
even after failures and rejects failed, cancelled or skipped required jobs.
Deployment depends on that gate and runs only on main. Pull requests and merge
queue events run validation without publishing. A green CodeQL job means analysis
completed; findings remain visible in code scanning and can be enforced by a
repository ruleset.

The aggregate shared Node/browser workflows target Node applications with required
lint/typecheck/build scripts and a local JavaScript Playwright dependency. This
repository uses Python build/browser scripts and npm only for axe-core, so the
project-check contract preserves the existing test tools. Docker publication,
PyPI publication, provider evaluations and Redis integration have no matching
artifact or runtime here.

`make ci-install` and `make ci-quality` reproduce the inherited project contract
locally. Browser dependencies and the optional CPU model environment have their
own pinned requirement files. The current acceptance report distinguishes checks
executed locally from any observed GitHub Actions run.
