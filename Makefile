.PHONY: clean test lint help

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

lint:
	flake8 --doctests --max-complexity 10 telegram

test:
	@- $(foreach TEST, $(wildcard tests/test_*.py), python $(TEST))

help:
	@echo "  clean		remove unwanted stuff"
	@echo "  lint		check style with flake8"
	@echo "  test		run tests"
