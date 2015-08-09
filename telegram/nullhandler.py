#!/usr/bin/env python


import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
