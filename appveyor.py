import os


def main():
    pyversion = os.environ.get('TRAVIS_PYTHON_VERSION', "didn't get it")
    print(pyversion)

if __name__=="__main__":
    main()