import os
import sys
import time

import requests
HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer vooe775fjw49jt0iu0d1'
    }

def build():
    pyversion = os.environ.get('TRAVIS_PYTHON_VERSION', "didn't get it")
    URL = 'https://ci.appveyor.com//api/builds'
    if pyversion == "pypy-5.3.1":
        pr = os.environ.get('TRAVIS_PULL_REQUEST', None)
        print("TRAVIS_PULL_REQUEST: {}".format(pr))
        if pr != 'false':
            PAYLOAD_APPVEYOR = {
                'accountName': 'Eldinnie',
                'projectSlug': 'python-telegram-bot-6akeh',
                'pullRequestId': pr
            }
            r = requests.post(URL, json=PAYLOAD_APPVEYOR, headers=HEADERS)
            print("Started build on Appveyor")
        else:
            branch = os.environ.get('TRAVIS_BRANCH', None)
            print("TRAVIS_BRANCH: {}".format(branch))
            commit_id = os.environ.get('TRAVIS_COMMIT', None)
            print("TRAVIS_COMMIT: {}".format(commit_id))
            PAYLOAD_APPVEYOR = {
                'accountName': 'Eldinnie',
                'projectSlug': 'python-telegram-bot-6akeh',
                'branch': branch,
                'commitId': commit_id
            }
            r = requests.post(URL, json=PAYLOAD_APPVEYOR, headers=HEADERS)
            print("Started build on Appveyor")


def wait():
    URL = 'https://ci.appveyor.com/api/projects/Eldinnie/python-telegram-bot-6akeh'
    print("checking if Appveyor is still running")
    r = requests.get(url=URL, headers=HEADERS)
    result = r.json()
    try:
        status = result['build']['status']
    except KeyError:
        status = ""
    if status != 'running':
        print('Appveyor is not working. Continue')
        sys.exit()
    else:
        print("Appveyor is running.")
        pr = str(os.environ.get('TRAVIS_PULL_REQUEST', None))
        print("TRAVIS_PULL_REQUEST: {}".format(pr))
        if pr != 'false':
            try:
                appveyor_pr = result['build']['pullRequestId']
            except KeyError:
                appveyor_pr = ''
            if pr == appveyor_pr:
                print("same pr in appveyor, shutting it down")
                version = result['build']['version']
                URL = "https://ci.appveyor.com/api/builds/Eldinnie/python-telegram-bot-6akeh/{}".format(version)
                r = requests.delete(URL, headers=HEADERS)
                sys.exit()
            else:
                waiting()
        else:
            branch = os.environ.get('TRAVIS_BRANCH', None)
            appveyor_branch = result['build']['branch']
            if branch == appveyor_branch:
                print("New commit on the same branch, canceling build on Appveyor")
                version = result['build']['version']
                URL = "https://ci.appveyor.com/api/builds/Eldinnie/python-telegram-bot-6akeh/{}".format(version)
                r = requests.delete(URL, headers=HEADERS)
                sys.exit()
            else:
                waiting()


def waiting():
    print("Appveyor working, waiting for completion.")
    while True:
        time.sleep(30)
        URL = 'https://ci.appveyor.com/api/projects/Eldinnie/python-telegram-bot-6akeh'
        r = requests.get(url=URL, headers=HEADERS)
        result = r.json()
        try:
            status = result['build']['status']
        except KeyError:
            status = ""
        if status != 'running':
            print('Appveyor is done. Continue')
            sys.exit()


if __name__ == "__main__":
    arg = sys.argv[1]
    if arg == 'build':
        build()
    if arg == 'wait':
        wait()
