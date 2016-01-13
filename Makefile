.PHONY: clean pep8 lint test install

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

pep257:
	pep257 telegram

pep8:
	flake8 telegram

lint:
	pylint -E telegram --disable=no-name-in-module,import-error

test:
	nosetests

install:
	pip install -r requirements.txt

help:
	@echo "Available targets:"
	@echo "- clean       Clean up the source directory"
	@echo "- pep257      Check docstring style with pep257"
	@echo "- pep8        Check style with flake8"
	@echo "- lint        Check style with pylint"
	@echo "- test        Run tests"
