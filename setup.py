#!/usr/bin/env python

'''The setup and build script for the python-telegram-bot library.'''

import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='python-telegram-bot',
    version='1.2',
    author='Leandro Toledo',
    author_email='leandrotoledodesouza@gmail.com',
    license='GPLv2',
    url='https://github.com/leandrotoledo/python-telegram-bot',
    keywords='telegram bot api',
    description='A Python wrapper around the Telegram Bot API',
    long_description=(read('README.rst')),
    packages=find_packages(exclude=['tests*']),
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
