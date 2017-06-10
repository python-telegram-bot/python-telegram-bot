import os
from urllib import request


def main():
    pyversion = os.environ.get('TRAVIS_PYTHON_VERSION', "didn't get it")
    HEADERS = {'Content-Type':'application/json'}
    URL = 'https://ci.appveyor.com//api/builds'
    if pyversion=="pypy-5.3.1":
        pr = os.environ.get('$TRAVIS_PULL_REQUEST', None)
        if pr:
            PAYLOAD_APPVEYOR = {
                'accountName': 'Eldinnie',
                'projectSlug': 'python-telegram-bot-6akeh',
                'pullRequestId': pr
            }
            print(request.Request(URL,data=PAYLOAD_APPVEYOR, headers=HEADERS, method='POST'))
        else:
            PAYLOAD_APPVEYOR = {
                'accountName': 'Eldinnie',
                'projectSlug': 'python-telegram-bot-6akeh',
                'branch': os.environ.get('$TRAVIS_BRANCH', None),
                'commitId': os.environ.get('TRAVIS_COMMIT', None)
            }
            print(request.Request(URL, data=PAYLOAD_APPVEYOR, headers=HEADERS, method='POST'))
if __name__=="__main__":
    main()