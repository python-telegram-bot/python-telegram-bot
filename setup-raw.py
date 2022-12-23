#!/usr/bin/env python
"""The setup and build script for the python-telegram-bot-raw library."""

from setuptools import setup

from setup import check_namespace_clashes, get_setup_kwargs

check_namespace_clashes(raw=True)
setup(**get_setup_kwargs(raw=True))
