from inspect import getmembers, ismethod
import threading
__all__ = ['CommandHandler','CommandHandlerWithHelp']

class CommandHandler(object):
    """ This handles incomming commands and gives an easy way to create commands.

    How to use this:
      create a new class which inherits this class or CommandHandlerWithHelp.
      define new methods that start with 'command_' and then the command_name.
      run run()
    """
    def __init__(self, bot):
        self.bot = bot  # a telegram bot

    def _get_command_func(self, command):
        if command[0] == '/':
            command = command[1:]
        if hasattr(self, 'command_' + command):
            return self.__getattribute__('command_' + command)  # a function
        else:
            return None

    def run(self, make_thread=True, last_update_id=None, thread_timeout=0):
        """Continuously check for commands and run the according method

        Args:
          make_thread:
            if True make a thread for each command it found.
            if False make run the code linearly
          last_update:
            the offset arg from getUpdates and is kept up to date within this function
          thread_timeout:
            The timeout on a thread. If a thread is alive after this period then try to join the thread in
            the next loop.
        """
        old_threads = []
        while True:
            threads, last_update_id = self.run_once(make_thread=make_thread, last_update_id=last_update_id)
            for t in threads:
                t.start()
            for t in old_threads:
                threads.append(t)
            old_threads = []
            for t in threads:
                t.join(timeout=thread_timeout)
                if t.isAlive():
                    old_threads.append(t)

    def run_once(self, make_thread=True, last_update_id=None):
        """ Check the the messages for commands and make a Thread with the command or run the command depending on make_thread.

        Args:
          make_thread:
            True: the function returns a list with threads. Which didn't start yet.
            False: the function just runs the command it found and returns an empty list.
          last_update_id:
            the offset arg from getUpdates and is kept up to date within this function

        Returns:
          A tuple of two elements. The first element is a list with threads which didn't start yet or an empty list if
          make_threads==False. The second element is the updated las_update_id
         """
        bot_name = self.bot.getMe().username
        threads = []
        for update in self.bot.getUpdates(offset=last_update_id):
            last_update_id = update.update_id + 1
            message = update.message
            if message.text[0] == '/':
                command, username = message.text.split(' ')[0], bot_name
                if '@' in command:
                    command, username = command.split('@')
                if username == bot_name:
                    command_func = self._get_command_func(command)
                    if command_func is not None:
                        if make_thread:
                            t = threading.Thread(target=command_func, args=(update,))
                            threads.append(t)
                        else:
                            command_func(update)
                    else:
                        if make_thread:
                            t = threading.Thread(target=self._command_not_found, args=(update,))
                            threads.append(t)
                        else:
                            self._command_not_found(update)
        return threads, last_update_id

    def _command_not_found(self, update):
        """Inform the telegram user that the command was not found.

        Override this method if you want to do it another way then by sending the the text:
        Sorry, I didn't understand the command: /command[@bot].
        """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = "Sorry, I didn't understand the command: {command}.".format(command=update.message.text.split(' ')[0])
        self.bot.sendMessage(chat_id, message, reply_to_message_id=reply_to)


class CommandHandlerWithHelp(CommandHandler):
    """ This CommandHandler has a builtin /help. It grabs the text from the docstrings of command_ functions."""
    def __init__(self, bot):
        super(CommandHandlerWithHelp, self).__init__(bot)
        self._help_title = 'Welcome to {name}.'.format(name=self.bot.getMe().username)  # the title of help
        self._help_before_list = ''  # text with information about the bot
        self._help_after_list = ''  # a footer
        self._help_list_title = 'These are the commands:'  # the title of the list
        self.is_reply = True
        self.command_start = self.command_help

    def _generate_help(self):
        """ Generate a string which can be send as a help file.

            This function generates a help file from all the docstrings from the commands.
            so docstrings of methods that start with command_ should explain what a command does and how a to use the
            command to the telegram user.
        """

        command_functions = [attr[1] for attr in getmembers(self, predicate=ismethod) if attr[0][:8] == 'command_']
        help_message = self._help_title + '\n\n'
        help_message += self._help_before_list + '\n\n'
        help_message += self._help_list_title + '\n'
        for command_function in command_functions:
            help_message += '  /' + command_function.__name__[8:] + ' - ' + command_function.__doc__ + '\n'
        help_message += '\n'
        help_message += self._help_after_list
        return help_message

    def _command_not_found(self, update):
        """Inform the telegram user that the command was not found."""
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = 'Sorry, I did not understand the command: {command}. Please see /help for all available commands'
        if self.is_reply:
            self.bot.sendMessage(chat_id=chat_id,
                                 message=message.format(command=update.message.text.split(' ')[0]),
                                 reply_to_message_id=reply_to)
        else:
            self.bot.sendMessage(chat_id, message.format(command=update.message.text.split(' ')[0]))

    def command_help(self, update):
        """ The help file. """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = self._generate_help()
        self.bot.sendMessage(chat_id, message, reply_to_message_id=reply_to)


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
