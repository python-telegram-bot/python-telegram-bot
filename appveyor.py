import os


def main():
    print(os.environ.get('TRAVIS_PYTHON_VERSIOn'))

if __name__=="__main__":
    main()