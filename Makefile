help:
	@echo "  env		create a development environment using virtualenv"
	@echo "  deps		install dependencies"
	@echo "  clean		remove unwanted stuff"
	@echo "  lint		check style with flake8"
	@echo "  test		run tests"

env:
	sudo easy_install pip && \
	pip install virtualenv && \
	virtualenv env && \
	. env/bin/activate && \
	make deps

deps:
	pip install -r requirements.txt

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

lint:
	flake8 telegram

test:
	python telegram_test.py
