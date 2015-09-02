# There could be some unused imports
from inspect import getmembers, ismethod
import threading
import logging
import telegram
import time
from telegram import CommandHandlerWithHelp, CommandHandler
class ExampleCommandHandler(CommandHandlerWithHelp):
    """This is an example how to use a CommandHandlerWithHelp or just a CommandHandler.

    If You want to use a CommandHandler it is very easy.
    create a class which inherits a CommandHandler.
    create a method in this class which start with 'command_' and takes 1 argument: 'update' (which comes directly from
    getUpdate()).
    If you inherit CommandHandlerWithHelp it also creates a nice /help for you.
    """
    def __init__(self, bot):  # only necessary for a WithHelp
        super(ExampleCommandHandler, self).__init__(bot)
        self._help_title = 'Welcome this is a help file!'  # optional
        self._help_before_list = """
        Yeah here I explain some things about this bot.
        and of course I can do this in Multiple lines.
        """  # default is empty
        self._help_list_title = ' These are the available commands:'  # optional
        self._help_after_list = ' These are some footnotes'  # default is empty
        self.is_reply = True  # default is True

    # only necessary if you want to override to default
    def _command_not_found(self, update):
        """Inform the telegram user that the command was not found."""
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = "Sorry, I don't know how to do {command}.".format(command=update.message.text.split(' ')[0])
        self.bot.sendMessage(chat_id, message, reply_to_message_id=reply_to)

    # creates /test command. This code gets called when a telegram user enters /test
    def command_test(self, update):
        """ Test if the server is online. """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = 'Yeah, the server is online!'
        self.bot.sendMessage(chat_id, message, reply_to_message_id=reply_to)

    # creates /parrot command
    def command_parrot(self, update):
        """ Says back what you say after the command"""
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        send = update.message.text.split(' ')
        message = update.message.text[len(send[0]):]
        if len(send) == 1:
            message = '...'
        self.bot.sendMessage(chat_id, message, reply_to_message_id=reply_to)

    # creates /p command
    def command_p(self, update):
        """Does the same as parrot."""
        return self.command_parrot(update)

    # this doesn't create a command.
    def another_test(self, update):
        """ This won't be called by the CommandHandler.

        This is an example of a function that isn't a command in telegram.
        Because it didn't start with 'command_'.
        """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = 'Yeah, this is another test'
        self.bot.sendMessage(chat_id, message, reply_to_message_id=reply_to)


class Exampe2CommandHandler(CommandHandler):
    """
    This is an example of a small working CommandHandler with only one command.
    """
    def command_test(self, update):
        """ Test if the server is online. """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = 'Yeah, the server is online!'
        self.bot.sendMessage(chat_id, message, reply_to_message_id=reply_to)

if __name__ == '__main__':
    import telegram
    token = ''  # use your own token here
    Bot = telegram.Bot(token=token)
    test_command_handler = ExampleCommandHandler(Bot)
    test_command_handler.run()
