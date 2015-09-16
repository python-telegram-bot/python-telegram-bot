import telegram


class NoSuchCommandException(BaseException):
    pass

class CommandDispatcher:
    def __init__(self,):
        self.commands = list()
        self.default = None

    def addCommand(self, command, callback):
        self.commands.append((command, callback))

    def setDefault(self, callback):
        self.default = callback

    def dispatch(self, update):
        if hasattr(update.message, 'text'):
            text = update.message.text
        else:
            text = ''

        user_id = update.message.from_user.id
        com = text.split('@')[0]
        for command, callback in self.commands:
            if com == command:
                return callback(command, user_id)
        if self.default is not None:
            return self.default(text, user_id)
        else:
            raise NoSuchCommandException()


class EnhancedBot(telegram.Bot):
    """The Bot class with command dispatcher added.

    >>> bot = EnhancedBot(token=TOKEN)
    >>> @bot.command('/start')
    ... def start(command, user_id):
    ...    # should return a tuple: (text, reply_id, custom_keyboard)
    ...    return ("Hello, there! Your id is {}".format(user_id), None, None)
    >>> while True:
    ...     bot.processUpdates()
    ...     time.sleep(3)
    """
    def __init__(self, token):
        self.dispatcher = CommandDispatcher()
        telegram.Bot.__init__(self, token=token)
        self.offset = 0 #id of the last processed update

    def command(self, *names, default=False):
        """Decorator for adding callbacks for commands."""

        def inner_command(callback):
            for name in names:
                self.dispatcher.addCommand(name, callback)
            if default:
                self.dispatcher.setDefault(callback)
            return callback # doesn't touch the callback, so we can use it
        return inner_command

    def processUpdates(self):
        updates = self.getUpdates(offset=self.offset)

        for update in updates:
            print('processing update: {}'.format(str(update.to_dict())))
            self.offset = update.update_id + 1
            if not hasattr(update, 'message'):
                continue

            try:
                answer, reply_to, reply_markup = self.dispatcher.dispatch(update)
            except Exception as e:
                print('error occured') # TODO logging
                print(update.to_dict())
                raise e

            if answer is not None:
                self.sendMessage(chat_id=update.message.chat_id,
                                 text=answer,
                                 reply_to_message_id=reply_to,
                                 reply_markup=reply_markup)
