# MVC BOT DEVELOPING:

In this folder we have a implementation of a *mvc* model for chat bots.
If your bot has complicated scenario I recommend you to use this model for your bot.
Also in this implementation every thing is an object an you can use **object oriented** features.

## Controller:
In this directory you can create classes that handle and control states of bot.
see [`test_controller.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/mvc_model_sample/controllers/test_controller.py)

## Model:
In this folder you can create your database tables (if you are using ORM) and other models.
see for example [`models.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/mvc_model_sample/model/models.py)

## View:

In this folder you can handle view of your messages, structure of messages and sending them.
see for example [`test_view.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/mvc_model_sample/view/test_view.py)