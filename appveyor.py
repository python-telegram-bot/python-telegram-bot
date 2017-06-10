import os


def main():
    print(os.environ.get('TRAVIS_PYTHON_VERSION', "didn't get it"))

if __name__=="__main__":
    main()