from __future__ import print_function

import subprocess
import sys
from platform import python_implementation
import inspect

import nose
from nose.config import Config
from nose.plugins import Plugin, DefaultPluginManager
from nose.plugins.cover import Coverage

import tests


class CustomCoverage(Coverage):
    enabled = True
    name = 'coverage'
    score = 201  # One higher than original package

    def report(self, stream):
        fold('coverage', 'Coverage report', stream=stream)
        super(CustomCoverage, self).report(stream)
        fold('coverage', stream=stream)


class FoldPlugin(Plugin):
    enabled = True
    name = 'travis-fold'
    score = 100

    def setOutputStream(self, stream):
        self.stream = stream

    def startContext(self, context):
        if inspect.ismodule(context) and context != tests:
            fold(context.__name__, context.__name__, stream=self.stream)

    def stopContext(self, context):
        if inspect.ismodule(context) and context != tests:
            fold(context.__name__, stream=self.stream)

folds = set()


def fold(foldname, comment=None, stream=sys.stdout):
    if foldname in folds:
        folds.remove(foldname)
        print('\ntravis_fold:end:{}'.format(foldname), file=stream, end='')
    else:
        folds.add(foldname)
        print('travis_fold:start:{}'.format(foldname), file=stream, end='')

    if comment:
        print('\n{}'.format(comment), file=stream)
    else:
        print('', file=stream)


def main():
    print('Starting...')
    fold('tests', 'Running tests...')
    config = Config(verbosity=2, plugins=DefaultPluginManager(), env={'NOSE_REDNOSE': '1'})
    tests = nose.run(argv=['--with-flaky', '--no-flaky-report',
                           '--with-coverage', '--cover-package=telegram/',
                           '--with-travis-fold',
                           'tests'],
                     addplugins=[FoldPlugin(), CustomCoverage()],
                     config=config)
    print('\n' * 2)
    if tests:
        fold('tests')

    # Only run pre-commit hooks once
    pre_commit = True
    if sys.version_info[:2] == (3, 6) and python_implementation() == 'CPython':
        fold('pre-commit', 'Running pre-commits')
        # TODO: Only run pre-commit hooks on changed files
        # Using something like git diff-tree and $TRAVIS_COMMIT_RANGE
        pre_commit = subprocess.call(['pre-commit', 'run', '--all-files']) == 0
        if pre_commit:
            fold('pre-commit')

    fold('bdist_dumb', 'Testing build...')
    # run_setup('setup.py', ['bdist_dumb'])  # Makes us unable to fetch exit code
    bdist_dumb = subprocess.call(['python', 'setup.py', 'bdist_dumb']) == 0
    if bdist_dumb:
        fold('bdist_dumb')

    sys.exit(0 if all((tests, pre_commit, bdist_dumb)) else 1)

if __name__ == '__main__':
    main()
