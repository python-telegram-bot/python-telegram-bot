import sys

import certifi
import future

from . import __version__ as telegram_ver


def print_ver_info():
    print('python-telegram-bot {0}'.format(telegram_ver))
    print('certifi {0}'.format(certifi.__version__))
    print('future {0}'.format(future.__version__))
    print('Python {0}'.format(sys.version.replace('\n', ' ')))


def main():
    print_ver_info()


if __name__ == '__main__':
    main()
