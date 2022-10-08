#!/usr/bin/env python
"""The setup and build script for the python-telegram-bot-raw library."""

from setuptools import setup

from setup import avoid_common_setup_errors, get_setup_kwargs

avoid_common_setup_errors(raw=True)
setup(**get_setup_kwargs(raw=True))
