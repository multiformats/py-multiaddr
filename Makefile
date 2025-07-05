.PHONY: clean-pyc clean-build docs clean
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

setup:
	pip install -r requirements_dev.txt

lint:
	python -m ruff check --fix

fix:
	python -m ruff check --fix

typecheck:
	pre-commit run pyright-pretty --all-files

test:
	python -m pytest tests

test-all:
	python3.11 -m pytest tests
	python3.13 -m pytest tests

coverage:
	coverage run --source multiaddr setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs:
	rm -f docs/multiaddr.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ multiaddr
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

.PHONY: authors
authors:
	git shortlog --numbered --summary --email | cut -f 2 > AUTHORS

dist: clean
	python -m build
	ls -l dist

install: clean
	python setup.py install

# build newsfragments into release notes and verify docs build correctly
notes: check-bump validate-newsfragments
	# Let UPCOMING_VERSION be the version that is used for the current bump
	$(eval UPCOMING_VERSION=$(shell bump-my-version bump --dry-run $(bump) -v | awk -F"'" '/New version will be / {print $$2}'))
	# Now generate the release notes to have them included in the release commit
	towncrier build --yes --version $(UPCOMING_VERSION)
	# Before we bump the version, make sure that the towncrier-generated docs will build
	make docs
	git commit -m "Compile release notes for v$(UPCOMING_VERSION)"

deploy-prep: clean authors docs dist
	@echo "Did you remember to bump the version?"
	@echo "If not, run 'bumpversion {patch, minor, major}' and run this target again"
	@echo "Don't forget to update HISTORY.rst"

# helpers

# verify that newsfragments are valid and towncrier can build them
validate-newsfragments:
	python ./newsfragments/validate_files.py
	towncrier build --draft --version preview

# verify that a bump argument is set to be passed to bump-my-version
check-bump:
ifndef bump
	$(error bump must be set, typically: major, minor, patch, or devnum)
endif
