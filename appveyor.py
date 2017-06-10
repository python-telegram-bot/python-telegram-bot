import os
import requests


def main():
    pyversion = os.environ.get('TRAVIS_PYTHON_VERSION', "didn't get it")
    HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer vooe775fjw49jt0iu0d1'
               }
    URL = 'https://ci.appveyor.com//api/builds'
    if pyversion=="pypy-5.3.1":
        pr = os.environ.get('$TRAVIS_PULL_REQUEST', None)
        if pr:
            PAYLOAD_APPVEYOR = {
                'accountName': 'Eldinnie',
                'projectSlug': 'python-telegram-bot-6akeh',
                'pullRequestId': pr
            }
            r = requests.post(URL, data=PAYLOAD_APPVEYOR, headers=HEADERS)
            print(r.json)
        else:
            PAYLOAD_APPVEYOR = {
                'accountName': 'Eldinnie',
                'projectSlug': 'python-telegram-bot-6akeh',
                'branch': os.environ.get('$TRAVIS_BRANCH', None),
                'commitId': os.environ.get('TRAVIS_COMMIT', None)
            }
            r = requests.post(URL, data=PAYLOAD_APPVEYOR, headers=HEADERS)
            print(r.json)

if __name__=="__main__":
    main()