=======
Changes
=======

**2017-07-25**
*Released 7.0.0*
- Fully support Bot API 3.2.
- Improved filters for user_id/username/chat (PR #677).
- Add the possibility to add objects as arguments to send_* methods (PR #742).
- Fixed download of URLs with UTF-8 chars in path (PR #688).
- Fixed URL parsing for ``Message`` text properties (PR #689).
- Fixed args dispatching in ``MessageQueue``'s decorator (PR #705).
-  ConvesationHandler - check if a user exist before using it (PR #699).
- Removed deprecated ``telegram.Emoji``.
- Removed deprecated ``Botan`` import from ``utils`` (``Botan`` is still available through ``contrib``).
- Removed deprecated ``ReplyKeyboardHide``.
- Removed deprecated ``edit_message`` argument of `bot.set_game_score``.
- Internal restructure of files.
- Improved documentation.
- Improved unitests.

**2017-06-18**

*Released 6.1.0*

- Fully support Bot API 3.0
- Add more fine-grained filters for status updates
- Bug fixes and other improvements

**2017-05-29**

*Released 6.0.3*

- Faulty PyPI release

**2017-05-29**

*Released 6.0.2*

- Avoid confusion with user's ``urllib3`` by renaming vendored ``urllib3`` to ``ptb_urllib3``

**2017-05-19**

*Released 6.0.1*

- Add support for ``User.language_code``
- Fix ``Message.text_html`` and ``Message.text_markdown`` for messages with emoji

**2017-05-19**

*Released 6.0.0*

- Add support for Bot API 2.3.1
- Add support for ``deleteMessage`` API method
- New, simpler API for ``JobQueue`` - https://github.com/python-telegram-bot/python-telegram-bot/pull/484
- Download files into file-like objects - https://github.com/python-telegram-bot/python-telegram-bot/pull/459
- Use vendor ``urllib3`` to address issues with timeouts
  - The default timeout for messages is now 5 seconds. For sending media, the default timeout is now 20 seconds.
- String attributes that are not set are now ``None`` by default, instead of empty strings
- Add ``text_markdown`` and ``text_html`` properties to ``Message`` - https://github.com/python-telegram-bot/python-telegram-bot/pull/507
- Add support for Socks5 proxy - https://github.com/python-telegram-bot/python-telegram-bot/pull/518
- Add support for filters in ``CommandHandler`` - https://github.com/python-telegram-bot/python-telegram-bot/pull/536
- Add the ability to invert (not) filters - https://github.com/python-telegram-bot/python-telegram-bot/pull/552
- Add ``Filters.group`` and ``Filters.private``
- Compatibility with GAE via ``urllib3.contrib`` package - https://github.com/python-telegram-bot/python-telegram-bot/pull/583
- Add equality rich comparision operators to telegram objects - https://github.com/python-telegram-bot/python-telegram-bot/pull/604
- Several bugfixes and other improvements
- Remove some deprecated code

**2017-04-17**

*Released 5.3.1*

- Hotfix release due to bug introduced by urllib3 version 1.21

**2016-12-11**

*Released 5.3*

- Implement API changes of November 21st (Bot API 2.3)
- ``JobQueue`` now supports ``datetime.timedelta`` in addition to seconds
- ``JobQueue`` now supports running jobs only on certain days
- New ``Filters.reply`` filter
- Bugfix for ``Message.edit_reply_markup``
- Other bugfixes

**2016-10-25**

*Released 5.2*

- Implement API changes of October 3rd (games update)
- Add ``Message.edit_*`` methods
- Filters for the ``MessageHandler`` can now be combined using bitwise operators (``& and |``)
- Add a way to save user- and chat-related data temporarily
- Other bugfixes and improvements

**2016-09-24**

*Released 5.1*

- Drop Python 2.6 support
- Deprecate ``telegram.Emoji``

- Use ``ujson`` if available
- Add instance methods to ``Message``, ``Chat``, ``User``, ``InlineQuery`` and ``CallbackQuery``
- RegEx filtering for ``CallbackQueryHandler`` and ``InlineQueryHandler``
- New ``MessageHandler`` filters: ``forwarded`` and ``entity``
- Add ``Message.get_entity`` to correctly handle UTF-16 codepoints and ``MessageEntity`` offsets
- Fix bug in ``ConversationHandler`` when first handler ends the conversation
- Allow multiple ``Dispatcher`` instances
- Add ``ChatMigrated`` Exception
- Properly split and handle arguments in ``CommandHandler``

**2016-07-15**

*Released 5.0*

- Rework ``JobQueue``
- Introduce ``ConversationHandler``
- Introduce ``telegram.constants`` - https://github.com/python-telegram-bot/python-telegram-bot/pull/342

**2016-07-12**

*Released 4.3.4*

- Fix proxy support with ``urllib3`` when proxy requires auth

**2016-07-08**

*Released 4.3.3*

- Fix proxy support with ``urllib3``

**2016-07-04**

*Released 4.3.2*

- Fix: Use ``timeout`` parameter in all API methods

**2016-06-29**

*Released 4.3.1*

- Update wrong requirement: ``urllib3>=1.10``

**2016-06-28**

*Released 4.3*

- Use ``urllib3.PoolManager`` for connection re-use
- Rewrite ``run_async`` decorator to re-use threads
- New requirements: ``urllib3`` and ``certifi``

**2016-06-10**

*Released 4.2.1*

- Fix ``CallbackQuery.to_dict()`` bug (thanks to @jlmadurga)
- Fix ``editMessageText`` exception when receiving a ``CallbackQuery``

**2016-05-28**

*Released 4.2*

- Implement Bot API 2.1
- Move ``botan`` module to ``telegram.contrib``
- New exception type: ``BadRequest``

**2016-05-22**

*Released 4.1.2*

- Fix ``MessageEntity`` decoding with Bot API 2.1 changes

**2016-05-16**

*Released 4.1.1*

- Fix deprecation warning in ``Dispatcher``

**2016-05-15**

*Released 4.1*

- Implement API changes from May 6, 2016
- Fix bug when ``start_polling`` with ``clean=True``
- Methods now have snake_case equivalent, for example ``telegram.Bot.send_message`` is the same as ``telegram.Bot.sendMessage``

**2016-05-01**

*Released 4.0.3*

- Add missing attribute ``location`` to ``InlineQuery``

**2016-04-29**

*Released 4.0.2*

- Bugfixes
- ``KeyboardReplyMarkup`` now accepts ``str`` again

**2016-04-27**

*Released 4.0.1*

- Implement Bot API 2.0
- Almost complete recode of ``Dispatcher``
- Please read the `Transition Guide to 4.0 <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-4.0>`_
- **Changes from 4.0rc1**
    - The syntax of filters for ``MessageHandler`` (upper/lower cases)
    - Handler groups are now identified by ``int`` only, and ordered
- **Note:** v4.0 has been skipped due to a PyPI accident

**2016-04-22**

*Released 4.0rc1*

- Implement Bot API 2.0
- Almost complete recode of ``Dispatcher``
- Please read the `Transistion Guide to 4.0 <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transistion-guide-to-Version-4.0>`_

**2016-03-22**

*Released 3.4*

- Move ``Updater``, ``Dispatcher`` and ``JobQueue`` to new ``telegram.ext`` submodule (thanks to @rahiel)
- Add ``disable_notification`` parameter (thanks to @aidarbiktimirov)
- Fix bug where commands sent by Telegram Web would not be recognized (thanks to @shelomentsevd)
- Add option to skip old updates on bot startup
- Send files from ``BufferedReader``

**2016-02-28**

*Released 3.3*

- Inline bots
- Send any file by URL
- Specialized exceptions: ``Unauthorized``, ``InvalidToken``, ``NetworkError`` and ``TimedOut``
- Integration for botan.io (thanks to @ollmer)
- HTML Parsemode (thanks to @jlmadurga)
- Bugfixes and under-the-hood improvements

**Very special thanks to Noam Meltzer (@tsnoam) for all of his work!**

**2016-01-09**

*Released 3.3b1*

- Implement inline bots (beta)

**2016-01-05**

*Released 3.2.0*

- Introducing ``JobQueue`` (original author: @franciscod)
- Streamlining all exceptions to ``TelegramError`` (Special thanks to @tsnoam)
- Proper locking of ``Updater`` and ``Dispatcher`` ``start`` and ``stop`` methods
- Small bugfixes

**2015-12-29**

*Released 3.1.2*

- Fix custom path for file downloads
- Don't stop the dispatcher thread on uncaught errors in handlers

**2015-12-21**

*Released 3.1.1*

- Fix a bug where asynchronous handlers could not have additional arguments
- Add ``groups`` and ``groupdict`` as additional arguments for regex-based handlers

**2015-12-16**

*Released 3.1.0*

- The ``chat``-field in ``Message`` is now of type ``Chat``. (API update Oct 8 2015)
- ``Message`` now contains the optional fields ``supergroup_chat_created``, ``migrate_to_chat_id``, ``migrate_from_chat_id`` and ``channel_chat_created``. (API update Nov 2015)

**2015-12-08**

*Released 3.0.0*

- Introducing the ``Updater`` and ``Dispatcher`` classes

**2015-11-11**

*Released 2.9.2*

- Error handling on request timeouts has been improved

**2015-11-10**

*Released 2.9.1*

- Add parameter ``network_delay`` to Bot.getUpdates for slow connections

**2015-11-10**

*Released 2.9*

- Emoji class now uses ``bytes_to_native_str`` from ``future`` 3rd party lib
- Make ``user_from`` optional to work with channels
- Raise exception if Telegram times out on long-polling

*Special thanks to @jh0ker for all hard work*


**2015-10-08**

*Released 2.8.7*

- Type as optional for ``GroupChat`` class


**2015-10-08**

*Released 2.8.6*

- Adds type to ``User`` and ``GroupChat`` classes (pre-release Telegram feature)


**2015-09-24**

*Released 2.8.5*

- Handles HTTP Bad Gateway (503) errors on request
- Fixes regression on ``Audio`` and ``Document`` for unicode fields


**2015-09-20**

*Released 2.8.4*

- ``getFile`` and ``File.download`` is now fully supported


**2015-09-10**

*Released 2.8.3*

- Moved ``Bot._requestURL`` to its own class (``telegram.utils.request``)
- Much better, such wow, Telegram Objects tests
- Add consistency for ``str`` properties on Telegram Objects
- Better design to test if ``chat_id`` is invalid
- Add ability to set custom filename on ``Bot.sendDocument(..,filename='')``
- Fix Sticker as ``InputFile``
- Send JSON requests over urlencoded post data
- Markdown support for ``Bot.sendMessage(..., parse_mode=ParseMode.MARKDOWN)``
- Refactor of ``TelegramError`` class (no more handling ``IOError`` or ``URLError``)


**2015-09-05**

*Released 2.8.2*

- Fix regression on Telegram ReplyMarkup
- Add certificate to ``is_inputfile`` method


**2015-09-05**

*Released 2.8.1*

- Fix regression on Telegram objects with thumb properties


**2015-09-04**

*Released 2.8*

- TelegramError when ``chat_id`` is empty for send* methods
- ``setWebhook`` now supports sending self-signed certificate
- Huge redesign of existing Telegram classes
- Added support for PyPy
- Added docstring for existing classes


**2015-08-19**

*Released 2.7.1*

- Fixed JSON serialization for ``message``


**2015-08-17**

*Released 2.7*

- Added support for ``Voice`` object and ``sendVoice`` method
- Due backward compatibility performer or/and title will be required for ``sendAudio``
- Fixed JSON serialization when forwarded message


**2015-08-15**

*Released 2.6.1*

- Fixed parsing image header issue on < Python 2.7.3


**2015-08-14**

*Released 2.6.0*

- Depreciation of ``require_authentication`` and ``clearCredentials`` methods
- Giving ``AUTHORS`` the proper credits for their contribution for this project
- ``Message.date`` and ``Message.forward_date`` are now ``datetime`` objects


**2015-08-12**

*Released 2.5.3*

- ``telegram.Bot`` now supports to be unpickled


**2015-08-11**

*Released 2.5.2*

- New changes from Telegram Bot API have been applied
- ``telegram.Bot`` now supports to be pickled
- Return empty ``str`` instead ``None`` when ``message.text`` is empty


**2015-08-10**

*Released 2.5.1*

- Moved from GPLv2 to LGPLv3


**2015-08-09**

*Released 2.5*

- Fixes logging calls in API


**2015-08-08**

*Released 2.4*

- Fixes ``Emoji`` class for Python 3
- ``PEP8`` improvements


**2015-08-08**

*Released 2.3*

- Fixes ``ForceReply`` class
- Remove ``logging.basicConfig`` from library


**2015-07-25**

*Released 2.2*

- Allows ``debug=True`` when initializing ``telegram.Bot``


**2015-07-20**

*Released 2.1*

- Fix ``to_dict`` for ``Document`` and ``Video``


**2015-07-19**

*Released 2.0*

- Fixes bugs
- Improves ``__str__`` over ``to_json()``
- Creates abstract class ``TelegramObject``


**2015-07-15**

*Released 1.9*

- Python 3 officially supported
- ``PEP8`` improvements


**2015-07-12**

*Released 1.8*

- Fixes crash when replying an unicode text message (special thanks to JRoot3D)


**2015-07-11**

*Released 1.7*

- Fixes crash when ``username`` is not defined on ``chat`` (special thanks to JRoot3D)


**2015-07-10**

*Released 1.6*

- Improvements for GAE support


**2015-07-10**

*Released 1.5*

- Fixes randomly unicode issues when using ``InputFile``


**2015-07-10**

*Released 1.4*

- ``requests`` lib is no longer required
- Google App Engine (GAE) is supported


**2015-07-10**

*Released 1.3*

- Added support to ``setWebhook`` (special thanks to macrojames)


**2015-07-09**

*Released 1.2*

- ``CustomKeyboard`` classes now available
- Emojis available
- ``PEP8`` improvements


**2015-07-08**

*Released 1.1*

- PyPi package now available


**2015-07-08**

*Released 1.0*

- Initial checkin of python-telegram-bot
