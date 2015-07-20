#!/usr/bin/env python
from .telegram_boject_base import Base


class ReplyMarkup(Base):
    def to_json(self):
        raise NotImplementedError
