# Examples
## ⚠️ The examples in this directory are subject to changes and may not work on the PTB version that you are using. You can find the examples compatible with a specific version at https://github.com/python-telegram-bot/python-telegram-bot/tree/v<X.Y>/examples

In this folder are small examples to show what a bot written with `python-telegram-bot` looks like. Some bots focus on one specific aspect of the Telegram Bot API while others focus on one of the mechanics of this library. Except for the [`rawapibot.py`](#pure-api) example, they all use the high-level framework this library provides with the [`telegram.ext`](https://docs.python-telegram-bot.org/telegram.ext.html) submodule.

All examples are licensed under the [CC0 License](LICENSE.txt) and are therefore fully dedicated to the public domain. You can use them as the base for your own bots without worrying about copyrights.

Do note that we ignore one pythonic convention. Best practice would dictate, in many handler callbacks function signatures, to replace the argument `context` with an underscore, since `context` is an unused local variable in those callbacks. However, since these are examples and not having a name for that argument confuses beginners, we decided to have it present.

### [`echobot.py`](echobot.py)
This is probably the base for most of the bots made with `python-telegram-bot`. It simply replies to each text message with a message that contains the same text.

### [`timerbot.py`](timerbot.py)
This bot uses the [`JobQueue`](https://docs.python-telegram-bot.org/telegram.ext.jobqueue.html) class to send timed messages. The user sets a timer by using `/set` command with a specific time, for example `/set 30`. The bot then sets up a job to send a message to that user after 30 seconds. The user can also cancel the timer by sending `/unset`. To learn more about the `JobQueue`, read [this wiki article](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-JobQueue).

### [`conversationbot.py`](conversationbot.py)
A common task for a bot is to ask information from the user. In v5.0 of this library, we introduced the [`ConversationHandler`](https://docs.python-telegram-bot.org/telegram.ext.conversationhandler.html) for that exact purpose. This example uses it to retrieve user-information in a conversation-like style. To get a better understanding, take a look at the [state diagram](conversationbot.png).

### [`conversationbot2.py`](conversationbot2.py)
A more complex example of a bot that uses the `ConversationHandler`. It is also more confusing. Good thing there is a [fancy state diagram](conversationbot2.png) for this one, too!

### [`nestedconversationbot.py`](nestedconversationbot.py)
A even more complex example of a bot that uses the nested `ConversationHandler`s. While it's certainly not that complex that you couldn't built it without nested `ConversationHanldler`s, it gives a good impression on how to work with them. Of course, there is a [fancy state diagram](nestedconversationbot.png) for this example, too!

### [`persistentconversationbot.py`](persistentconversationbot.py)
A basic example of a bot store conversation state and user_data over multiple restarts.

### [`inlinekeyboard.py`](inlinekeyboard.py)
This example sheds some light on inline keyboards, callback queries and message editing. A wiki site explaining this examples lives [here](https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example).

### [`inlinekeyboard2.py`](inlinekeyboard2.py)
A more complex example about inline keyboards, callback queries and message editing. This example showcases how an interactive menu could be build using inline keyboards.

### [`deeplinking.py`](deeplinking.py)
A basic example on how to use deeplinking with inline keyboards.

### [`inlinebot.py`](inlinebot.py)
A basic example of an [inline bot](https://core.telegram.org/bots/inline). Don't forget to enable inline mode with [@BotFather](https://t.me/BotFather).

### [`pollbot.py`](pollbot.py)
This example sheds some light on polls, poll answers and the corresponding handlers.

### [`passportbot.py`](passportbot.py)
A basic example of a bot that can accept passports. Use in combination with [`passportbot.html`](passportbot.html). Don't forget to enable and configure payments with [@BotFather](https://t.me/BotFather). Check out this [guide](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Telegram-Passport) on Telegram passports in PTB.

### [`paymentbot.py`](paymentbot.py)
A basic example of a bot that can accept payments. Don't forget to enable and configure payments with [@BotFather](https://t.me/BotFather).

### [`errorhandlerbot.py`](errorhandlerbot.py)
A basic example on how to set up a custom error handler.

### [`chatmemberbot.py`](chatmemberbot.py)
A basic example on how `(my_)chat_member` updates can be used.

### [`webappbot.py`](webappbot.py)
A basic example of how [Telegram WebApps](https://core.telegram.org/bots/webapps) can be used.
Use in combination with [`webappbot.html`](webappbot.html).
For your convenience, this file is hosted by the PTB team such that you don't need to host it yourself.
Uses the [`iro.js`](https://iro.js.org) JavaScript library to showcase a user interface that is hard to achieve with native Telegram functionality.

### [`contexttypesbot.py`](contexttypesbot.py)
This example showcases how `telegram.ext.ContextTypes` can be used to customize the `context` argument of handler and job callbacks.

### [`customwebhookbot.py`](customwebhookbot.py)
This example showcases how a custom webhook setup can be used in combination with `telegram.ext.Application`.

### [`arbitrarycallbackdatabot.py`](arbitrarycallbackdatabot.py)
This example showcases how PTBs "arbitrary callback data" feature can be used.

## Pure API
The [`rawapibot.py`](rawapibot.py) example uses only the pure, "bare-metal" API wrapper.
