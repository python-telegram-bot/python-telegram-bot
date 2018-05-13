from uuid import uuid4

from telegram import InlineQueryResultArticle
from telegram.ext import InlineQueryHandler
from tgintegration import BotIntegrationClient


class TestInlinequeriesIntegration(object):
    @staticmethod
    def create_handler(title, message_text, pattern=None):

        id_ = str(uuid4())

        def cb(bot, update):
            bot.answer_inline_query()
            results = [
                InlineQueryResultArticle(
                    id_,
                    title,
                    input_message_content=message_text,
                )
            ]
            update.inline_query.answer(results)

        return InlineQueryHandler(cb, pattern=pattern)

    def test_basic(self, dp, client: BotIntegrationClient):

        handler = self.create_handler("test", "text")
        dp.add_handler(handler)

        res = client.get_inline_results("gimme any")
        print(res.find_results(title_pattern=r'test'))
        assert res.find_results(title_pattern=r'test')
