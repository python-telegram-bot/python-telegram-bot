Games
-----

Your bot can offer users **HTML5 games** to play solo or to compete against each other in groups and one-on-one chats. Create games via `@BotFather`_ using the /*newgame* command. Please note that this kind of power requires responsibility: you will need to accept the terms for each game that your bots will be offering.

* Games are a new type of content on Telegram, represented by the `Game`_ and `InlineQueryResultGame`_ objects.
* Once you've created a game via `BotFather`_, you can send games to chats as regular messages using the `sendGame`_ method, or use `inline mode`_ with `InlineQueryResultGame`_.
* If you send the game message without any buttons, it will automatically have a 'Play *GameName*' button. When this button is pressed, your bot gets a `CallbackQuery`_ with the *game_short_name* of the requested game. You provide the correct URL for this particular user and the app opens the game in the in-app browser.
* You can manually add multiple buttons to your game message. Please note that the first button in the first row **must always** launch the game, using the field *callback_game* in `InlineKeyboardButton`_. You can add extra buttons according to taste: e.g., for a description of the rules, or to open the game's official community.
* To make your game more attractive, you can upload a GIF animation that demostrates the game to the users via `BotFather`_ (see `Lumberjack`_ for example).
* A game message will also display high scores for the current chat. Use `setGameScore`_ to post high scores to the chat with the game, add the edit_message parameter to automatically update the message with the current scoreboard.
* Use `getGameHighScores`_ to get data for in-game high score tables.
* You can also add an extra `sharing button`_ for users to share their best score to different chats.
* For examples of what can be done using this new stuff, check the `@gamebot`_ and `@gamee`_ bots.

.. _@BotFather: https://t.me/botfather
.. _Game: https://docs.python-telegram-bot.org/en/v21.4/telegram.game.html
.. _InlineQueryResultGame: https://docs.python-telegram-bot.org/en/v21.4/telegram.inlinequeryresultgame.html
.. _BotFather: https://t.me/botfather
.. _sendGame: https://core.telegram.org/bots/api#sendgame
.. _inline mode: https://docs.python-telegram-bot.org/en/v21.4/telegram.inline-tree.html
.. _CallbackQuery: https://docs.python-telegram-bot.org/en/v21.4/telegram.callbackquery.html
.. _InlineKeyboardButton: https://docs.python-telegram-bot.org/en/v21.4/telegram.inlinekeyboardbutton.html
.. _Lumberjack: https://t.me/gamebot?game=lumberjack
.. _setGameScore: https://core.telegram.org/bots/api#setgamescore
.. _getGameHighScores: https://core.telegram.org/bots/api#getgamehighscores
.. _sharing button: https://core.telegram.org/bots/games#sharing-your-game-to-telegram-chats
.. _@gamebot: https://t.me/gamebot
.. _@gamee: https://t.me/gamee


.. toctree::
    :titlesonly:

    telegram.callbackgame
    telegram.game
    telegram.gamehighscore
