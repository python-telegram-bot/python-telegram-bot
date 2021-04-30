#!/usr/bin/env python
"""The setup and build script for the python-telegram-bot-raw library."""

from setuptools import setup
from setup import get_setup_kwargs

setup(**get_setup_kwargs(raw=True))
