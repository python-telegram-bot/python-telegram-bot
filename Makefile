help:
	@echo "  clean		remove unwanted stuff"
	@echo "  lint		check style with flake8"
	@echo "  test		run tests"

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

lint:
	flake8 --doctests --max-complexity 10 telegram

test:
	python telegram_test.py
