from telegram.ext import Updater

from controller.test_controller import TestController
from database_connect import engine, Base

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    updater = Updater(token="YOUR_BOT_TOKEN")
    dispatcher = updater.dispatcher
    test_controller = TestController(dispatcher=dispatcher)
    updater.start_polling(poll_interval=1)
    updater.idle()
