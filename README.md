# RAG and AI full-stack learning guide

Open [index.html](index.html) to use the interactive, self-contained guide: 300 interview questions across 30 chapters, searchable answers, local notes and bookmarks, print mode, examples, diagrams, and line-addressable source snapshots. It is a static site; no server, package install, model key, or backend is needed.

## GitHub Pages

The workflow in `.github/workflows/pages.yml` publishes the site from the `main` branch. Push this repository to a new GitHub repository, then select **Settings → Pages → GitHub Actions** if Pages is not already configured. The workflow also supports manual runs. Project site links are relative and work under the repository subpath.

**Visibility:** a private source repository does not make a GitHub Pages site private. GitHub Pages sites are public by default, and private site access is limited to supported GitHub Enterprise Cloud organization configurations. This guide includes frozen source code from the Ragnor project and an insurance backend. Review whether that source may be shared before enabling deployment. The repository itself can remain private while the published site is public.

## Study data

Progress, theme, bookmarks, and notes are stored in browser local storage. Export progress for backup. Treat exports as private if notes contain personal information.

## Contents

This repository is the static learning-guide site. `sources/` contains frozen, line-addressable project excerpts, and `diagrams/` contains the explorable diagram pages used by the guide. The original host repositories are not included. See [provenance](provenance.html) for source revisions, scope, and limitations.
