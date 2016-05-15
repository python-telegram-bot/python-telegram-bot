.DEFAULT_GOAL := help
.PHONY: clean pep257 pep8 yapf lint test install

PYLINT          := pylint
NOSETESTS       := nosetests
PEP257          := pep257
PEP8            := flake8
YAPF            := yapf
PIP             := pip

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;
	find . -regex "./telegram.\(mp3\|mp4\|ogg\|png\|webp\)" -exec rm {} \;

pep257:
	$(PEP257) telegram

pep8:
	$(PEP8) telegram

yapf:
	$(YAPF) -r telegram

lint:
	$(PYLINT) -E telegram --disable=no-name-in-module,import-error

test:
	$(NOSETESTS) -v

install:
	$(PIP)  install -r requirements.txt -r requirements-dev.txt

help:
	@echo "Available targets:"
	@echo "- clean       Clean up the source directory"
	@echo "- pep257      Check docstring style with pep257"
	@echo "- pep8        Check style with flake8"
	@echo "- lint        Check style with pylint"
	@echo "- yapf        Check style with yapf"
	@echo "- test        Run tests"
	@echo
	@echo "Available variables:"
	@echo "- PYLINT      default: $(PYLINT)"
	@echo "- NOSETESTS   default: $(NOSETESTS)"
	@echo "- PEP257      default: $(PEP257)"
	@echo "- PEP8        default: $(PEP8)"
	@echo "- YAPF        default: $(YAPF)"
	@echo "- PIP         default: $(PIP)"
