from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters


class TestController:
    """
    TestController class:
        The main responsibility of this class is 'controlling states of bot with user inputs and handlers', etc.
        It depends on your bot scenario you can create a main controller class for starting bot and common states of
        your bot and then create some other controller classes and inherit from main controller class.

    """

    states_dict = {
        "step_1": 1,
        "step_2": 2
    }

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.__process_handlers()

    def main_menu(self, bot, update):
        chat_id = update.message.chat.id
        bot.send_message(chat_id=chat_id, text="main menu!")
        return self.states_dict["step_1"]

    def first_step(self, bot, update):
        chat_id = update.message.chat.id
        bot.send_message(chat_id=chat_id, text="hello first step!")
        return self.states_dict["step_2"]

    def final_step(self, bot, update):
        chat_id = update.message.chat.id
        bot.send_message(chat_id=chat_id, text="hello final step!")
        return ConversationHandler.END

    def __process_handlers(self):
        conversation_handler = ConversationHandler(entry_points=[CommandHandler("/start", self.main_menu)],
                                                   states={
                                                       self.states_dict["step_1"]: [
                                                           MessageHandler(Filters.text, self.final_step)],
                                                       self.states_dict["step_2"]: [
                                                           MessageHandler(Filters.photo, self.final_step)]
                                                   }, fallbacks=[], allow_reentry=True)
        self.dispatcher.add_handler(conversation_handler)
