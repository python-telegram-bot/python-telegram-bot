import sys
sys.path.append('.')
import telegram
import unittest
import unittest.mock
from telegram.command_handler import CommandHandler, CommandHandlerWithHelp


class CommandHandlerTmp(CommandHandler):
    def __init__(self, *args, **kwargs):
        super(CommandHandlerTmp, self).__init__(*args, **kwargs)
        self.output = None

    def command_test(self, update):
        self.output = 1


class CommandHandlerTmp2(CommandHandlerWithHelp):
    def __init__(self, *args, **kwargs):
        super(CommandHandlerTmp2, self).__init__(*args, **kwargs)
        self.output_test = None

    def command_test(self, update):
        self.output_test = 1


def fake_getUpdates(*args, **kwargs):
    from_user = telegram.User(id=42, first_name='hello')
    message = telegram.Message(message_id=42, from_user=from_user, date=None, chat=from_user, text='/test')
    update = telegram.Update(update_id=42, message=message)
    return [update]

output_fsm = None


def fake_sendMessage(chat_id, message, *args, **kwargs):
    global output_fsm
    output_fsm = (chat_id, message)
    return telegram.Message(43, 123, 000000, telegram.User(chat_id, 'test'), text=message)


class CommandHandlerTest(unittest.TestCase):
    def setUp(self):
        self.bot = unittest.mock.MagicMock()
        self.bot.getUpdates = fake_getUpdates
        self.bot.sendMessage = fake_sendMessage

    def test_get_command_func(self):
        CH = CommandHandlerTmp(self.bot)
        self.assertEqual(CH.command_test, CH._get_command_func('test'))
        self.assertEqual(CH.command_test, CH._get_command_func('/test'))
        self.assertEqual(None, CH._get_command_func('this function does not exsist'))

    def test_run_once(self):
        CH = CommandHandlerTmp(self.bot)
        self.assertEqual(CH.output, None)
        threads, last_update = CH.run_once(make_thread=True)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(CH.output, 1)

    def test_run(self):
        pass  # TODO implement test

    def test__command_not_found(self):
        CH = CommandHandlerTmp(self.bot)
        CH._command_not_found(self.bot.getUpdates()[0])
        self.assertEqual(output_fsm, (42, "Sorry, I didn't understand the command: /test."))


if __name__ == '__main__':
    import sys
    unittest.main(sys.argv)
