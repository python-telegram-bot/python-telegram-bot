import inspect
from utils.utils import get_logger

logger = get_logger()


class MessageSender:
    def __init__(self, bot):
        self.bot = bot

    def send_message(self, chat_id, text, reply_markup=None):
        self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        logger.info(inspect.stack()[1][3])
