PYTHON ?= $(shell command -v python3.11 2>/dev/null || command -v python3)
PORT ?= 8765
.DEFAULT_GOAL := help

.PHONY: help build package site check serve clean runtime ci-install ci-quality

# Contract consumed by the SHA-pinned shared project-check workflow.
ci-install: runtime

ci-quality: check

help:
	@echo "make site   - build and package the public site"
	@echo "make check  - rebuild, package, and verify content and examples"
	@echo "make serve  - rebuild and preview at http://127.0.0.1:$(PORT)"
	@echo "make clean  - remove generated output only"
	@echo "Override PYTHON=python3.11 or PORT=8767 when needed."

runtime:
	$(PYTHON) -B scripts/vendor_pyodide.py

build:
	$(PYTHON) -B scripts/build.py

package: build
	$(PYTHON) -B scripts/package.py

site: package

check: site
	$(PYTHON) -B tests/check.py

serve: site
	$(PYTHON) -m http.server $(PORT) --bind 127.0.0.1 --directory _site

clean:
	$(PYTHON) -c 'from pathlib import Path; import shutil; [shutil.rmtree(p) for p in (Path("_build"), Path("_site")) if p.exists()]'
