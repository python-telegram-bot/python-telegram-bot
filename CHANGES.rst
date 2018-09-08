=======
Changes
=======

**2018-09-01**
*Released 11.1.0*

Fixes and updates for Telegram Passport: (`#1198`_)

- Fix passport decryption failing at random times
- Added support for middle names.
- Added support for translations for documents
- Add errors for translations for documents
- Added support for requesting names in the language of the user's country of residence
- Replaced the payload parameter with the new parameter nonce
- Add hash to EncryptedPassportElement

.. _`#1198`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1198

**2018-08-29**
*Released 11.0.0*

Fully support Bot API version 4.0!
(also some bugfixes :))

Telegram Passport (`#1174`_):

- Add full support for telegram passport.
    - New types: PassportData, PassportFile, EncryptedPassportElement, EncryptedCredentials, PassportElementError, PassportElementErrorDataField, PassportElementErrorFrontSide, PassportElementErrorReverseSide, PassportElementErrorSelfie, PassportElementErrorFile and PassportElementErrorFiles.
    - New bot method: set_passport_data_errors
    - New filter: Filters.passport_data
    - Field passport_data field on Message
    - PassportData can be easily decrypted.
    - PassportFiles are automatically decrypted if originating from decrypted PassportData.
- See new passportbot.py example for details on how to use, or go to `our telegram passport wiki page`_ for more info
- NOTE: Passport decryption requires new dependency `cryptography`.

Inputfile rework (`#1184`_):

- Change how Inputfile is handled internally
- This allows support for specifying the thumbnails of photos and videos using the thumb= argument in the different send\_ methods.
- Also allows Bot.send_media_group to actually finally send more than one media.
- Add thumb to Audio, Video and Videonote
- Add Bot.edit_message_media together with InputMediaAnimation, InputMediaAudio, and inputMediaDocument.

Other Bot API 4.0 changes:

- Add forusquare_type to Venue, InlineQueryResultVenue, InputVenueMessageContent, and Bot.send_venue. (`#1170`_)
- Add vCard support by adding vcard field to Contact, InlineQueryResultContact, InputContactMessageContent, and Bot.send_contact. (`#1166`_)
- Support new message entities: CASHTAG and PHONE_NUMBER. (`#1179`_)
    - Cashtag seems to be things like `$USD` and `$GBP`, but it seems telegram doesn't currently send them to bots.
    - Phone number also seems to have limited support for now
- Add Bot.send_animation, add width, height, and duration to Animation, and add Filters.animation. (`#1172`_)

Non Bot API 4.0 changes:

- Minor integer comparison fix (`#1147`_)
- Fix Filters.regex failing on non-text message (`#1158`_)
- Fix ProcessLookupError if process finishes before we kill it (`#1126`_)
- Add t.me links for User, Chat and Message if available and update User.mention_* (`#1092`_)
- Fix mention_markdown/html on py2 (`#1112`_)

.. _`#1092`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1092
.. _`#1112`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1112
.. _`#1126`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1126
.. _`#1147`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1147
.. _`#1158`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1158
.. _`#1166`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1166
.. _`#1170`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1170
.. _`#1174`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1174
.. _`#1172`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1172
.. _`#1179`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1179
.. _`#1184`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1184
.. _`our telegram passport wiki page`: https://git.io/fAvYd

**2018-05-02**
*Released 10.1.0*

Fixes changing previous behaviour:

- Add urllib3 fix for socks5h support (`#1085`_)
- Fix send_sticker() timeout=20 (`#1088`_)

Fixes:

- Add a caption_entity filter for filtering caption entities (`#1068`_)
- Inputfile encode filenames (`#1086`_)
- InputFile: Fix proper naming of file when reading from subprocess.PIPE (`#1079`_)
- Remove pytest-catchlog from requirements (`#1099`_)
- Documentation fixes (`#1061`_, `#1078`_, `#1081`_, `#1096`_)

.. _`#1061`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1061
.. _`#1068`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1068
.. _`#1078`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1078
.. _`#1079`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1079
.. _`#1081`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1081
.. _`#1085`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1085
.. _`#1086`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1086
.. _`#1088`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1088
.. _`#1096`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1096
.. _`#1099`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1099

**2018-04-17**
*Released 10.0.2*

Important fix:

- Handle utf8 decoding errors (`#1076`_)

New features:

- Added Filter.regex (`#1028`_)
- Filters for Category and file types (`#1046`_)
- Added video note filter (`#1067`_)

Fixes:

- Fix in telegram.Message (`#1042`_)
- Make chat_id a positional argument inside shortcut methods of Chat and User classes (`#1050`_)
- Make Bot.full_name return a unicode object. (`#1063`_)
- CommandHandler faster check (`#1074`_)
- Correct documentation of Dispatcher.add_handler (`#1071`_)
- Various small fixes to documentation.

.. _`#1028`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1028
.. _`#1042`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1042
.. _`#1046`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1046
.. _`#1050`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1050
.. _`#1067`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1067
.. _`#1063`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1063
.. _`#1074`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1074
.. _`#1076`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1076
.. _`#1071`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1071

**2018-03-05**
*Released 10.0.1*

Fixes:

- Fix conversationhandler timeout (PR `#1032`_)
- Add missing docs utils (PR `#912`_)

.. _`#1032`: https://github.com/python-telegram-bot/python-telegram-bot/pull/826
.. _`#912`: https://github.com/python-telegram-bot/python-telegram-bot/pull/826

**2018-03-02**
*Released 10.0.0*

Non backward compatabile changes and changed defaults

- JobQueue: Remove deprecated prevent_autostart & put() (PR `#1012`_)
- Bot, Updater: Remove deprecated network_delay (PR `#1012`_)
- Remove deprecated Message.new_chat_member (PR `#1012`_)
- Retry bootstrap phase indefinitely (by default) on network errors (PR `#1018`_)

New Features

- Support v3.6 API (PR `#1006`_)
- User.full_name convinience property (PR `#949`_)
- Add `send_phone_number_to_provider` and `send_email_to_provider` arguments to send_invoice (PR `#986`_)
- Bot: Add shortcut methods reply_{markdown,html} (PR `#827`_)
- Bot: Add shortcut method reply_media_group (PR `#994`_)
- Added utils.helpers.effective_message_type (PR `#826`_)
- Bot.get_file now allows passing a file in addition to file_id (PR `#963`_)
- Add .get_file() to Audio, Document, PhotoSize, Sticker, Video, VideoNote and Voice (PR `#963`_)
- Add .send_*() methods to User and Chat (PR `#963`_)
- Get jobs by name (PR `#1011`_)
- Add Message caption html/markdown methods (PR `#1013`_)
- File.download_as_bytearray - new method to get a d/led file as bytearray (PR `#1019`_)
- File.download(): Now returns a meaningful return value (PR `#1019`_)
- Added conversation timeout in ConversationHandler (PR `#895`_)

Changes

- Store bot in PreCheckoutQuery (PR `#953`_)
- Updater: Issue INFO log upon received signal (PR `#951`_)
- JobQueue: Thread safety fixes (PR `#977`_)
- WebhookHandler: Fix exception thrown during error handling (PR `#985`_)
- Explicitly check update.effective_chat in ConversationHandler.check_update (PR `#959`_)
- Updater: Better handling of timeouts during get_updates (PR `#1007`_)
- Remove unnecessary to_dict() (PR `#834`_)
- CommandHandler - ignore strings in entities and "/" followed by whitespace (PR `#1020`_)
- Documentation & style fixes (PR `#942`_, PR `#956`_, PR `#962`_, PR `#980`_, PR `#983`_)

.. _`#826`: https://github.com/python-telegram-bot/python-telegram-bot/pull/826
.. _`#827`: https://github.com/python-telegram-bot/python-telegram-bot/pull/827
.. _`#834`: https://github.com/python-telegram-bot/python-telegram-bot/pull/834
.. _`#895`: https://github.com/python-telegram-bot/python-telegram-bot/pull/895
.. _`#942`: https://github.com/python-telegram-bot/python-telegram-bot/pull/942
.. _`#949`: https://github.com/python-telegram-bot/python-telegram-bot/pull/949
.. _`#951`: https://github.com/python-telegram-bot/python-telegram-bot/pull/951
.. _`#956`: https://github.com/python-telegram-bot/python-telegram-bot/pull/956
.. _`#953`: https://github.com/python-telegram-bot/python-telegram-bot/pull/953
.. _`#962`: https://github.com/python-telegram-bot/python-telegram-bot/pull/962
.. _`#959`: https://github.com/python-telegram-bot/python-telegram-bot/pull/959
.. _`#963`: https://github.com/python-telegram-bot/python-telegram-bot/pull/963
.. _`#977`: https://github.com/python-telegram-bot/python-telegram-bot/pull/977
.. _`#980`: https://github.com/python-telegram-bot/python-telegram-bot/pull/980
.. _`#983`: https://github.com/python-telegram-bot/python-telegram-bot/pull/983
.. _`#985`: https://github.com/python-telegram-bot/python-telegram-bot/pull/985
.. _`#986`: https://github.com/python-telegram-bot/python-telegram-bot/pull/986
.. _`#994`: https://github.com/python-telegram-bot/python-telegram-bot/pull/994
.. _`#1006`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1006
.. _`#1007`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1007
.. _`#1011`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1011
.. _`#1012`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1012
.. _`#1013`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1013
.. _`#1018`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1018
.. _`#1019`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1019
.. _`#1020`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1020

**2017-12-08**
*Released 9.0.0*

Breaking changes (possibly)

- Drop support for python 3.3 (PR `#930`_)


New Features

- Support Bot API 3.5 (PR `#920`_)


Changes

- Fix race condition in dispatcher start/stop (`#887`_)
- Log error trace if there is no error handler registered (`#694`_)
- Update examples with consistent string formatting (`#870`_)
- Various changes and improvements to the docs.

.. _`#920`: https://github.com/python-telegram-bot/python-telegram-bot/pull/920
.. _`#930`: https://github.com/python-telegram-bot/python-telegram-bot/pull/930
.. _`#887`: https://github.com/python-telegram-bot/python-telegram-bot/pull/887
.. _`#694`: https://github.com/python-telegram-bot/python-telegram-bot/pull/694
.. _`#870`: https://github.com/python-telegram-bot/python-telegram-bot/pull/870

**2017-10-15**
*Released 8.1.1*

- Fix Commandhandler crashing on single character messages (PR `#873`_).

.. _`#873`: https://github.com/python-telegram-bot/python-telegram-bot/pull/871

**2017-10-14**
*Released 8.1.0*

New features
- Support Bot API 3.4 (PR `#865`_).

Changes
- MessageHandler & RegexHandler now consider channel_updates.
- Fix command not recognized if it is directly followed by a newline (PR `#869`_).
- Removed Bot._message_wrapper (PR `#822`_).
- Unitests are now also running on AppVeyor (Windows VM).
- Various unitest improvements.
- Documentation fixes.

.. _`#822`: https://github.com/python-telegram-bot/python-telegram-bot/pull/822
.. _`#865`: https://github.com/python-telegram-bot/python-telegram-bot/pull/865
.. _`#869`: https://github.com/python-telegram-bot/python-telegram-bot/pull/869

**2017-09-01**
*Released 8.0.0*

New features

- Fully support Bot Api 3.3 (PR `#806`_).
- DispatcherHandlerStop (`see docs`_).
- Regression fix for text_html & text_markdown (PR `#777`_).
- Added effective_attachment to message (PR `#766`_).

Non backward compatible changes

- Removed Botan support from the library  (PR `#776`_).
- Fully support Bot Api 3.3 (PR `#806`_).
- Remove de_json() (PR `#789`_).

Changes

- Sane defaults for tcp socket options on linux (PR `#754`_).
- Add RESTRICTED as constant to ChatMember (PR `#761`_).
- Add rich comparison to CallbackQuery (PR `#764`_).
- Fix get_game_high_scores (PR `#771`_).
- Warn on small con_pool_size during custom initalization of Updater (PR `#793`_).
- Catch exceptions in error handlerfor errors that happen during polling (PR `#810`_).
- For testing we switched to pytest (PR `#788`_).
- Lots of small improvements to our tests and documentation.


.. _`see docs`: http://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.dispatcher.html#telegram.ext.Dispatcher.add_handler
.. _`#777`: https://github.com/python-telegram-bot/python-telegram-bot/pull/777
.. _`#806`: https://github.com/python-telegram-bot/python-telegram-bot/pull/806
.. _`#766`: https://github.com/python-telegram-bot/python-telegram-bot/pull/766
.. _`#776`: https://github.com/python-telegram-bot/python-telegram-bot/pull/776
.. _`#789`: https://github.com/python-telegram-bot/python-telegram-bot/pull/789
.. _`#754`: https://github.com/python-telegram-bot/python-telegram-bot/pull/754
.. _`#761`: https://github.com/python-telegram-bot/python-telegram-bot/pull/761
.. _`#764`: https://github.com/python-telegram-bot/python-telegram-bot/pull/764
.. _`#771`: https://github.com/python-telegram-bot/python-telegram-bot/pull/771
.. _`#788`: https://github.com/python-telegram-bot/python-telegram-bot/pull/788
.. _`#793`: https://github.com/python-telegram-bot/python-telegram-bot/pull/793
.. _`#810`: https://github.com/python-telegram-bot/python-telegram-bot/pull/810

**2017-07-28**
*Released 7.0.1*

- Fix TypeError exception in RegexHandler (PR #751).
- Small documentation fix (PR #749).

**2017-07-25**
*Released 7.0.0*

- Fully support Bot API 3.2.
- New filters for handling messages from specific chat/user id (PR #677).
- Add the possibility to add objects as arguments to send_* methods (PR #742).
- Fixed download of URLs with UTF-8 chars in path (PR #688).
- Fixed URL parsing for ``Message`` text properties (PR #689).
- Fixed args dispatching in ``MessageQueue``'s decorator (PR #705).
- Fixed regression preventing IPv6 only hosts from connnecting to Telegram servers (Issue #720).
- ConvesationHandler - check if a user exist before using it (PR #699).
- Removed deprecated ``telegram.Emoji``.
- Removed deprecated ``Botan`` import from ``utils`` (``Botan`` is still available through ``contrib``).
- Removed deprecated ``ReplyKeyboardHide``.
- Removed deprecated ``edit_message`` argument of ``bot.set_game_score``.
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
