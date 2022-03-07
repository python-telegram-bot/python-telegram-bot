#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram.ext import (
    ApplicationBuilder,
    PersistenceInput,
)


class TestPersistenceIntegration:
    # TODO:
    #  * Test add_handler with persistent conversationhandler
    #  * Test migrate_chat_data
    #  * Test drop_chat/user_data
    #  * Test update_persistence & flush getting called on shutdown
    #  * Test the update parameter of create_task

    def test_construction_with_bad_persistence(self, caplog, bot):
        class MyPersistence:
            def __init__(self):
                self.store_data = PersistenceInput(False, False, False, False)

        with pytest.raises(
            TypeError, match='persistence must be based on telegram.ext.BasePersistence'
        ):
            ApplicationBuilder().bot(bot).persistence(MyPersistence()).build()

    #
    # def test_error_while_saving_chat_data(self, bot):
    #     increment = []
    #
    #     class OwnPersistence(BasePersistence):
    #         def get_callback_data(self):
    #             return None
    #
    #         def update_callback_data(self, data):
    #             raise Exception
    #
    #         def get_bot_data(self):
    #             return {}
    #
    #         def update_bot_data(self, data):
    #             raise Exception
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def get_chat_data(self):
    #             return defaultdict(dict)
    #
    #         def update_chat_data(self, chat_id, data):
    #             raise Exception
    #
    #         def get_user_data(self):
    #             return defaultdict(dict)
    #
    #         def update_user_data(self, user_id, data):
    #             raise Exception
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def start1(u, c):
    #         pass
    #
    #     def error(u, c):
    #         increment.append("error")
    #
    #     # If updating a user_data or chat_data from a persistence object throws an error,
    #     # the error handler should catch it
    #
    #     update = Update(
    #         1,
    #         message=Message(
    #             1,
    #             None,
    #             Chat(1, "lala"),
    #             from_user=User(1, "Test", False),
    #             text='/start',
    #             entities=[
    #                 MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #             ],
    #             bot=bot,
    #         ),
    #     )
    #     my_persistence = OwnPersistence()
    #     app = ApplicationBuilder().bot(bot).persistence(my_persistence).build()
    #     app.add_handler(CommandHandler('start', start1))
    #     app.add_error_handler(error)
    #     app.process_update(update)
    #     assert increment == ["error", "error", "error", "error"]
    #
    # def test_error_while_persisting(self, app, caplog):
    #     class OwnPersistence(BasePersistence):
    #         def update(self, data):
    #             raise Exception('PersistenceError')
    #
    #         def update_callback_data(self, data):
    #             self.update(data)
    #
    #         def update_bot_data(self, data):
    #             self.update(data)
    #
    #         def update_chat_data(self, chat_id, data):
    #             self.update(data)
    #
    #         def update_user_data(self, user_id, data):
    #             self.update(data)
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def get_chat_data(self):
    #             pass
    #
    #         def get_bot_data(self):
    #             pass
    #
    #         def get_user_data(self):
    #             pass
    #
    #         def get_callback_data(self):
    #             pass
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def callback(update, context):
    #         pass
    #
    #     test_flag = []
    #
    #     def error(update, context):
    #         nonlocal test_flag
    #         test_flag.append(str(context.error) == 'PersistenceError')
    #         raise Exception('ErrorHandlingError')
    #
    #     update = Update(
    #         1, message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')
    #     )
    #     handler = MessageHandler(filters.ALL, callback)
    #     app.add_handler(handler)
    #     app.add_error_handler(error)
    #
    #     app.persistence = OwnPersistence()
    #
    #     with caplog.at_level(logging.ERROR):
    #         app.process_update(update)
    #
    #     assert test_flag == [True, True, True, True]
    #     assert len(caplog.records) == 4
    #     for record in caplog.records:
    #         message = record.getMessage()
    #         assert message.startswith('An error was raised and an uncaught')
    #
    # def test_persisting_no_user_no_chat(self, app):
    #     class OwnPersistence(BasePersistence):
    #         def __init__(self):
    #             super().__init__()
    #             self.test_flag_bot_data = False
    #             self.test_flag_chat_data = False
    #             self.test_flag_user_data = False
    #
    #         def update_bot_data(self, data):
    #             self.test_flag_bot_data = True
    #
    #         def update_chat_data(self, chat_id, data):
    #             self.test_flag_chat_data = True
    #
    #         def update_user_data(self, user_id, data):
    #             self.test_flag_user_data = True
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def get_user_data(self):
    #             pass
    #
    #         def get_bot_data(self):
    #             pass
    #
    #         def get_chat_data(self):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def get_callback_data(self):
    #             pass
    #
    #         def update_callback_data(self, data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def callback(update, context):
    #         pass
    #
    #     handler = MessageHandler(filters.ALL, callback)
    #     app.add_handler(handler)
    #     app.persistence = OwnPersistence()
    #
    #     update = Update(
    #         1, message=Message(1, None, None, from_user=User(1, '', False), text='Text')
    #     )
    #     app.process_update(update)
    #     assert app.persistence.test_flag_bot_data
    #     assert app.persistence.test_flag_user_data
    #     assert not app.persistence.test_flag_chat_data
    #
    #     app.persistence.test_flag_bot_data = False
    #     app.persistence.test_flag_user_data = False
    #     app.persistence.test_flag_chat_data = False
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert app.persistence.test_flag_bot_data
    #     assert not app.persistence.test_flag_user_data
    #     assert app.persistence.test_flag_chat_data
    #
    # def test_update_persistence_all_async(self, monkeypatch, app):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #
    #     for group in range(5):
    #         app.add_handler(
    #             MessageHandler(filters.TEXT, dummy_callback, block=True), group=group
    #         )
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert self.count == 0
    #
    #     app.bot._defaults = Defaults(block=True)
    #     try:
    #         for group in range(5):
    #             app.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)
    #
    #         update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None,
    #         text='Text'))
    #         app.process_update(update)
    #         assert self.count == 0
    #     finally:
    #         app.bot._defaults = None
    #
    # @pytest.mark.parametrize('block', [DEFAULT_FALSE, False])
    # def test_update_persistence_one_sync(self, monkeypatch, app, block):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #
    #     for group in range(5):
    #         app.add_handler(
    #             MessageHandler(filters.TEXT, dummy_callback, block=True), group=group
    #         )
    #     app.add_handler(MessageHandler(filters.TEXT, dummy_callback, block=block),group=5)
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert self.count == 1
    #
    # @pytest.mark.parametrize('block,expected', [(DEFAULT_FALSE, 1), (False, 1), (True, 0)])
    # def test_update_persistence_defaults_async(self, monkeypatch, app, block, expected):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #     app.bot._defaults = Defaults(block=block)
    #
    #     try:
    #         for group in range(5):
    #             app.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)
    #
    #         update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None,
    #         text='Text'))
    #         app.process_update(update)
    #         assert self.count == expected
    #     finally:
    #         app.bot._defaults = None
