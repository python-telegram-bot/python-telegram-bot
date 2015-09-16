from inspect import getmembers, ismethod
import threading
import logging
import telegram
import time
logger = logging.getLogger(__name__)
__all__ = ['CommandHandler', 'CommandHandlerWithHelp', 'CommandHandlerWithFatherCommand',
           'CommandHandlerWithHelpAndFather']


class CommandHandler(object):
    """ This handles incomming commands and gives an easy way to create commands.

    How to use this:
      create a new class which inherits this class or CommandHandlerWithHelp.
      define new methods that start with 'command_' and then the command_name.
      run run()
    """
    def __init__(self, bot):
        self.bot = bot  # a telegram bot
        self.isValidCommand = None  # a function that returns a boolean and takes one agrument an update.
                                    # If False is returned the the command is not executed.

    def _get_command_func(self, command):
        if command[0] == '/':
            command = command[1:]
        if hasattr(self, 'command_' + command):
            return self.__getattribute__('command_' + command)  # a function
        else:
            return None

    def run(self, make_thread=True, last_update_id=None, thread_timeout=2, sleep=0.2):
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
            time.sleep(sleep)
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
        try:
            updates = self.bot.getUpdates(offset=last_update_id)
        except:
            updates = []
        for update in updates:
            last_update_id = update.update_id + 1
            message = update.message
            if message.text[0] == '/':
                command, username = message.text.split(' ')[0], bot_name
                if '@' in command:
                    command, username = command.split('@')
                if username == bot_name:
                    command_func = self._get_command_func(command)
                    if command_func is not None:
                        self.bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)
                        if self.isValidCommand is None or self.isValidCommand(update):
                            if make_thread:
                                t = threading.Thread(target=command_func, args=(update,))
                                threads.append(t)
                            else:
                                command_func(update)
                        else:
                            self._command_not_found(update)  # TODO this must be another function.
                    else:
                        if make_thread:
                            t = threading.Thread(target=self._command_not_found, args=(update,))
                            threads.append(t)
                        else:
                            self._command_not_valid(update)
        return threads, last_update_id

    def _command_not_valid(self, update):
        """Inform the telegram user that the command was not found.

        Override this method if you want to do it another way then by sending the the text:
        Sorry, I didn't understand the command: /command[@bot].
        """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = "Sorry, the command was not authorised or valid: {command}.".format(
            command=update.message.text.split(' ')[0])
        self.bot.sendMessage(chat_id=chat_id, text=message, reply_to_message_id=reply_to)

    def _command_not_found(self, update):
        """Inform the telegram user that the command was not found.

        Override this method if you want to do it another way then by sending the the text:
        Sorry, I didn't understand the command: /command[@bot].
        """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = "Sorry, I didn't understand the command: {command}.".format(command=update.message.text.split(' ')[0])
        self.bot.sendMessage(chat_id=chat_id, text=message, reply_to_message_id=reply_to)


class CommandHandlerWithHelp(CommandHandler):
    """ This CommandHandler has a builtin /help. It grabs the text from the docstrings of command_ functions."""
    def __init__(self, bot):
        super(CommandHandlerWithHelp, self).__init__(bot)
        self._help_title = 'Welcome to {name}.'.format(name=self.bot.getMe().username)  # the title of help
        self._help_before_list = ''  # text with information about the bot
        self._help_after_list = ''  # a footer
        self._help_list_title = 'These are the commands:'  # the title of the list
        self._help_extra_message = 'These commands are only usefull to the developer.'
        self.is_reply = True
        self.command_start = self.command_help
        self.skip_in_help = []
    
    def command_helpextra(self,update):
        """ The commands in here are only usefull to the developer of the bot"""
        command_functions = [attr[1] for attr in getmembers(self, predicate=ismethod) if attr[0][:8] == 'command_' and
                             attr[0] in self.skip_in_help]
        chat_id = update.message.chat.id
        help_message = self._help_extra_message + '\n'
        for command_function in command_functions:
            if command_function.__doc__ is not None:
                help_message += '  /' + command_function.__name__[8:] + ' - ' + command_function.__doc__ + '\n'
            else:
                help_message += '  /' + command_function.__name__[8:] + ' - ' + '\n'
        self.bot.sendMessage(chat_id=chat_id, text=help_message)

    def _generate_help(self):
        """ Generate a string which can be send as a help file.

            This function generates a help file from all the docstrings from the commands.
            so docstrings of methods that start with command_ should explain what a command does and how a to use the
            command to the telegram user.
        """

        help_message = self._help_title + '\n\n'
        help_message += self._help_before_list + '\n\n'
        help_message += self._help_list_title + '\n'
        help_message += self._generate_help_list()
        help_message += '\n'
        help_message += self._help_after_list
        return help_message
    
    def _generate_help_list(self):
        command_functions = [attr[1] for attr in getmembers(self, predicate=ismethod) if attr[0][:8] == 'command_' and
                             attr[0] not in self.skip_in_help]
        help_message = ''
        for command_function in command_functions:
            if command_function.__doc__ is not None:
                help_message += '  /' + command_function.__name__[8:] + ' - ' + command_function.__doc__ + '\n'
            else:
                help_message += '  /' + command_function.__name__[8:] + ' - ' + '\n'
        return help_message

    def _command_not_found(self, update):
        """Inform the telegram user that the command was not found."""
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = 'Sorry, I did not understand the command: {command}. Please see /help for all available commands'
        if self.is_reply:
            self.bot.sendMessage(chat_id=chat_id, text=message.format(command=update.message.text.split(' ')[0]),
                                 reply_to_message_id=reply_to)
        else:
            self.bot.sendMessage(chat_id=chat_id, text=message.format(command=update.message.text.split(' ')[0]))

    def command_help(self, update):
        """ The help file. """
        chat_id = update.message.chat.id
        reply_to = update.message.message_id
        message = self._generate_help()
        self.bot.sendMessage(chat_id=chat_id, text=message, reply_to_message_id=reply_to)


class CommandHandlerWithFatherCommand(CommandHandler):
    """ A class that creates some commands that are usefull when setting up the bot
    """
    def __init__(self, bot):
        super(CommandHandlerWithFatherCommand, self).__init__(bot)
        self.skip_in_help = ['command_father']

    def command_father(self, update):
        """Gives you the commands you need to setup this bot. in telegram.me/BotFather"""
        chat_id = update.message.chat.id
        self.bot.sendMessage(chat_id=chat_id, text='Send the following messages to telegram.me/BotFather')
        self.bot.sendMessage(chat_id=chat_id, text='/setcommands')
        self.bot.sendMessage(chat_id=chat_id, text='@' + self.bot.getMe()['username'])
        commands = ''
        command_functions = [attr[1] for attr in getmembers(self, predicate=ismethod) if attr[0][:8] == 'command_' and
                             attr[0] not in self.skip_in_help]
    
        for command_function in command_functions:
            if command_function.__doc__ is not None:
                commands += command_function.__name__[8:] + ' - ' + command_function.__doc__ + '\n'
            else:
                commands += command_function.__name__[8:] + ' - ' + '\n'
        self.bot.sendMessage(chat_id=chat_id, text=commands)


class CommandHandlerWithHelpAndFather(CommandHandlerWithFatherCommand, CommandHandlerWithHelp):
    """A class that combines CommandHandlerWithHelp and CommandHandlerWithFatherCommand.
    """
    pass
