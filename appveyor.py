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
        pr = os.environ.get('TRAVIS_PULL_REQUEST', None)
        print("TRAVIS_PULL_REQUEST: {}".format(pr))
        if pr:
            PAYLOAD_APPVEYOR = {
                'accountName': 'Eldinnie',
                'projectSlug': 'python-telegram-bot-6akeh',
                'pullRequestId': pr
            }
            r = requests.post(URL, data=PAYLOAD_APPVEYOR, headers=HEADERS)
            print(r.json())
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
            r = requests.post(URL, data=PAYLOAD_APPVEYOR, headers=HEADERS)
            print(r.json())

if __name__=="__main__":
    main()