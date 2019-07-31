from view.message_sender import MessageSender


class TestView:

    """
    TestView class:
        the main responsibility of this class is 'sending messages of each state in bot'
        and also 'formatting of messages', etc.

    """

    main_menu_text = "main menu text!"
    first_step_text = "hello first step!"
    final_step_text = "hello final step!"

    def __init__(self, bot):
        self.message_sender = MessageSender(bot=bot)

    def send_main_menu_message(self, chat_id):
        self.message_sender.send_message(chat_id=chat_id, text=self.main_menu_text)

    def send_first_step_message(self, chat_id):
        self.message_sender.send_message(chat_id=chat_id, text=self.first_step_text)

    def send_final_step_message(self, chat_id):
        self.message_sender.send_message(chat_id=chat_id, text=self.final_step_text)
