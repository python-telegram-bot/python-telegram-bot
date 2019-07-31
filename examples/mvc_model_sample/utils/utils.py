import logging


def add_handlers(dispatcher, handlers):
    for handler in handlers:
        dispatcher.add_handler(handler)


def get_logger():
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    return logger
