VERSION=$(shell cat VERSION)

all:
	@echo "make test - Run tests"
	@echo "make release - Build and upload package and docs to PyPI"
	@echo "make source - Create source package"
	@echo "make docs - Build html documentation"
	@echo "make clean"
.PHONY: all

docclean:
	rm -rf docs/_build
.PHONY: docclean

clean: docclean
	-python setup.py clean
	rm -rf build/ MANIFEST
	rm -rf .tox
	rm -rf dist/*
	find . -name '*.pyc' -or -name '__pycache__' | xargs rm -rf
	(which dh_clean && dh_clean) || true
.PHONY: clean

lint:
	tox -e lint
.PHONY: lint

test:
	@echo Starting tests...
	tox
.PHONY: test

ftest:
	@echo Starting fast tests...
	tox -- --attr '!slow'
.PHONY: ftest

docs: lint
	(cd docs; make html SPHINXBUILD=../.tox/py3/bin/sphinx-build)
.PHONY: docs

source: test
	.tox/py3/bin/python setup.py sdist
.PHONY: source

release: test docs
	git remote | xargs -L1 git fetch --tags
	.tox/py3/bin/python setup.py sdist register upload upload_docs
	git tag release-${VERSION}
	git remote | xargs -L1 git push --tags
.PHONY: release

docrelease: ftest docs
	.tox/py3/bin/python setup.py sdist register upload_docs
.PHONY: docrelease
