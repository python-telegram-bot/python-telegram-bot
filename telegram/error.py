#!/usr/bin/env python


class TelegramError(Exception):
    """Base class for Telegram errors."""

    @property
    def message(self):
        '''Returns the first argument used to construct this error.'''
        return self.args[0]
