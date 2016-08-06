# coding: utf-8
"""
This module contains a simple integration with django.

To install on your django project, you need to register all bots on settings, add one line on
your urls and create a register method that will received a dispatcher to add all handlers of
your bot.

///////// settings.py

TELEGRAM_BOT = [{
    'token': '{YOUR_BOT_TOKEN}',
    'register': 'myapp.dispatcher.register',  # register method that will be called
    'webhook': 'https://mydomain.com/telegram_webhook/%s'  # optional if you use django.sites
}]

/////////  urls.py file

urlpatterns = [
    ...
    url(r'^telegram_webhook/', include('telegram.contrib.django',)),
    ...
]

/// myapp/dispatcher.py

from telegram.ext import CommandHandler

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi from telegram bot inside django project!')

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='This is a help message')

def error(bot, update):
    bot.sendMessage(update.message.chat_id, text='Command not founded.')

# this method will be called on start of application
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dp.add_error_handler(error)

"""

import json
import logging

try:
    import django
except ImportError as e:
    raise Exception('Need Django installed.')

from telegram import Bot
from telegram import Update
from telegram.ext import Dispatcher

from django.conf.urls import url
from django.http import HttpResponse
from django.views import generic
from django.conf import settings
from django.http.response import Http404
from django.utils.module_loading import import_string
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

BOTS_REGISTERED = {}

@method_decorator(csrf_exempt, name='dispatch')
class TelegramView(generic.View):

    @classmethod
    def as_view(cls, **initkwargs):
        register_webhooks()
        return super(TelegramView, cls).as_view(**initkwargs)

    def get(self, request):
        return HttpResponse()

    def head(self, request):
        return HttpResponse()

    def post(self, request, token):
        dispatcher = self.get_dispatcher(token)
        if not dispatcher:
            return Http404()

        json_string = request.body.decode('utf-8')
        update = Update.de_json(json.loads(json_string))
        dispatcher.process_update(update)
        return HttpResponse()

    def get_dispatcher(self, token):
        dispatcher = None
        if token in BOTS_REGISTERED:
            return BOTS_REGISTERED[token]
        return dispatcher


class DjangoDispatcher(Dispatcher):

    def __init__(self, bot):
        self.bot = bot

        self.handlers = {}
        """:type: dict[int, list[Handler]"""
        self.groups = []
        """:type: list[int]"""
        self.error_handlers = []

        self.logger = logging.getLogger(__name__)

    def start(self):
        self.logger.warning('DjangoDispatcher do not need start or thread.')


def register_webhooks(force=False):
    global BOTS_REGISTERED
    if BOTS_REGISTERED or not force:
        return

    BOTS_REGISTERED = {}

    for bot_config in settings.TELEGRAM_BOT:
        bot = Bot(bot_config['token'])

        if 'webhook' in bot_config:
            url = bot_config['webhook'] % bot.token
            if url[-1] != '/':
                url += '/'
        else:
            webhook = reverse('telegram_webhook', kwargs={'token': bot.token})
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            url = 'https://' + current_site.domain + webhook

        bot.set_webhook(url)
        bot = Bot(bot_config['token'])
        dispatcher = DjangoDispatcher(bot)
        register = import_string(bot_config['register'])
        register(dispatcher)
        BOTS_REGISTERED[bot.token] = dispatcher
        logger.info('bot %s registered on url %s', bot.token, url)

urlpatterns = [
    url(r'^(?P<token>[-_:a-zA-Z0-9]+)/$', TelegramView.as_view(), name='telegram_webhook'),
]