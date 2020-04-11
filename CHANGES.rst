=========
Changelog
=========

Version 12.6.1
==============
*Released 2020-04-11*

**Bug fixes:**

- Fix serialization of ``reply_markup`` in media messages (`#1889`_)

.. _`#1889`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1889

Version 12.6
============
*Released 2020-04-10*

**Major Changes:**

- Bot API 4.7 support. **Note:** In ``Bot.create_new_sticker_set`` and ``Bot.add_sticker_to_set``, the order of the parameters had be changed, as the ``png_sticker`` parameter is now optional. (`#1858`_)

**Minor changes, CI improvements or bug fixes:**

- Add tests for ``swtich_inline_query(_current_chat)`` with empty string (`#1635`_)
- Doc fixes (`#1854`_, `#1874`_, `#1884`_)
- Update issue templates (`#1880`_)
- Favor concrete types over "Iterable" (`#1882`_)
- Pass last valid ``CallbackContext`` to ``TIMEOUT`` handlers of ``ConversationHandler`` (`#1826`_)
- Tweak handling of persistence and update persistence after job calls (`#1827`_)
- Use checkout@v2 for GitHub actions (`#1887`_)

.. _`#1858`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1858
.. _`#1635`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1635
.. _`#1854`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1854
.. _`#1874`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1874
.. _`#1884`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1884
.. _`#1880`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1880
.. _`#1882`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1882
.. _`#1826`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1826
.. _`#1827`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1827
.. _`#1887`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1887

Version 12.5.1
==============
*Released 2020-03-30*

**Minor changes, doc fixes or bug fixes:**

- Add missing docs for `PollHandler` and `PollAnswerHandler` (`#1853`_)
- Fix wording in `Filters` docs (`#1855`_)
- Reorder tests to make them more stable (`#1835`_)
- Make `ConversationHandler` attributes immutable (`#1756`_)
- Make `PrefixHandler` attributes `command` and `prefix` editable (`#1636`_)
- Fix UTC as default `tzinfo` for `Job` (`#1696`_)

.. _`#1853`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1853
.. _`#1855`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1855
.. _`#1835`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1835
.. _`#1756`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1756
.. _`#1636`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1636
.. _`#1696`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1696

Version 12.5
============
*Released 2020-03-29*

**New Features:**

- `Bot.link` gives the `t.me` link of the bot (`#1770`_)

**Major Changes:**

- Bot API 4.5 and 4.6 support. (`#1508`_, `#1723`_)

**Minor changes, CI improvements or bug fixes:**

- Remove legacy CI files (`#1783`_, `#1791`_)
- Update pre-commit config file (`#1787`_)
- Remove builtin names (`#1792`_)
- CI improvements (`#1808`_, `#1848`_)
- Support Python 3.8 (`#1614`_, `#1824`_)
- Use stale bot for auto closing stale issues (`#1820`_, `#1829`_, `#1840`_)
- Doc fixes (`#1778`_, `#1818`_)
- Fix typo in `edit_message_media` (`#1779`_)
- In examples, answer CallbackQueries and use `edit_message_text` shortcut (`#1721`_)
- Revert accidental change in vendored urllib3 (`#1775`_)

.. _`#1783`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1783
.. _`#1787`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1787
.. _`#1792`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1792
.. _`#1791`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1791
.. _`#1808`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1808
.. _`#1614`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1614
.. _`#1770`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1770
.. _`#1824`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1824
.. _`#1820`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1820
.. _`#1829`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1829
.. _`#1840`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1840
.. _`#1778`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1778
.. _`#1779`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1779
.. _`#1721`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1721
.. _`#1775`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1775
.. _`#1848`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1848
.. _`#1818`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1818
.. _`#1508`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1508
.. _`#1723`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1723

Version 12.4.2
==============
*Released 2020-02-10*

**Bug Fixes**

- Pass correct parse_mode to InlineResults if bot.defaults is None (`#1763`_)
- Make sure PP can read files that dont have bot_data (`#1760`_)

.. _`#1763`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1763
.. _`#1760`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1760

Version 12.4.1
==============
*Released 2020-02-08*

This is a quick release for `#1744`_ which was accidently left out of v12.4.0 though mentioned in the
release notes.


Version 12.4.0
==============
*Released 2020-02-08*

**New features:**

- Set default values for arguments appearing repeatedly. We also have a `wiki page for the new defaults`_. (`#1490`_)
- Store data in ``CallbackContext.bot_data`` to access it in every callback. Also persists. (`#1325`_)
- ``Filters.poll`` allows only messages containing a poll (`#1673`_)

**Major changes:**

- ``Filters.text`` now accepts messages that start with a slash, because ``CommandHandler`` checks for ``MessageEntity.BOT_COMMAND`` since v12. This might lead to your MessageHandlers receiving more updates than before (`#1680`_).
- ``Filters.command`` new checks for ``MessageEntity.BOT_COMMAND`` instead of just a leading slash. Also by ``Filters.command(False)`` you can now filters for messages containing a command `anywhere` in the text (`#1744`_).

**Minor changes, CI improvements or bug fixes:**

- Add ``disptacher`` argument to ``Updater`` to allow passing a customized ``Dispatcher`` (`#1484`_)
- Add missing names for ``Filters`` (`#1632`_)
- Documentation fixes (`#1624`_, `#1647`_, `#1669`_, `#1703`_, `#1718`_, `#1734`_, `#1740`_, `#1642`_, `#1739`_, `#1746`_)
- CI improvements (`#1716`_, `#1731`_, `#1738`_, `#1748`_, `#1749`_, `#1750`_, `#1752`_)
- Fix spelling issue for ``encode_conversations_to_json`` (`#1661`_)
- Remove double assignement of ``Dispatcher.job_queue`` (`#1698`_)
- Expose dispatcher as property for ``CallbackContext`` (`#1684`_)
- Fix ``None`` check in ``JobQueue._put()`` (`#1707`_)
- Log datetimes correctly in ``JobQueue`` (`#1714`_)
- Fix false ``Message.link`` creation for private groups (`#1741`_)
- Add option ``--with-upstream-urllib3`` to `setup.py` to allow using non-vendored version (`#1725`_)
- Fix persistence for nested ``ConversationHandlers`` (`#1679`_)
- Improve handling of non-decodable server responses (`#1623`_)
- Fix download for files without ``file_path`` (`#1591`_)
- test_webhook_invalid_posts is now considered flaky and retried on failure (`#1758`_)

.. _`wiki page for the new defaults`: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Adding-defaults-to-your-bot
.. _`#1744`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1744
.. _`#1752`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1752
.. _`#1750`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1750
.. _`#1591`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1591
.. _`#1490`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1490
.. _`#1749`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1749
.. _`#1623`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1623
.. _`#1748`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1748
.. _`#1679`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1679
.. _`#1711`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1711
.. _`#1325`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1325
.. _`#1746`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1746
.. _`#1725`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1725
.. _`#1739`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1739
.. _`#1741`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1741
.. _`#1642`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1642
.. _`#1738`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1738
.. _`#1740`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1740
.. _`#1734`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1734
.. _`#1680`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1680
.. _`#1718`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1718
.. _`#1714`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1714
.. _`#1707`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1707
.. _`#1731`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1731
.. _`#1673`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1673
.. _`#1684`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1684
.. _`#1703`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1703
.. _`#1698`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1698
.. _`#1669`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1669
.. _`#1661`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1661
.. _`#1647`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1647
.. _`#1632`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1632
.. _`#1624`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1624
.. _`#1716`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1716
.. _`#1484`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1484
.. _`#1758`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1484

Version 12.3.0
==============
*Released 2020-01-11*

**New features:**

- `Filters.caption` allows only messages with caption (`#1631`_).
- Filter for exact messages/captions with new capability of `Filters.text` and `Filters.caption`. Especially useful in combination with ReplyKeyboardMarkup. (`#1631`_).

**Major changes:**

- Fix inconsistent handling of naive datetimes (`#1506`_).

**Minor changes, CI improvements or bug fixes:**

- Documentation fixes (`#1558`_, `#1569`_, `#1579`_, `#1572`_, `#1566`_, `#1577`_, `#1656`_).
- Add mutex protection on `ConversationHandler` (`#1533`_).
- Add `MAX_PHOTOSIZE_UPLOAD` constant (`#1560`_).
- Add args and kwargs to `Message.forward()` (`#1574`_).
- Transfer to GitHub Actions CI (`#1555`_, `#1556`_, `#1605`_, `#1606`_, `#1607`_, `#1612`_, `#1615`_, `#1645`_).
- Fix deprecation warning with Py3.8 by vendored urllib3 (`#1618`_).
- Simplify assignements for optional arguments (`#1600`_)
- Allow private groups for `Message.link` (`#1619`_).
- Fix wrong signature call for `ConversationHandler.TIMEOUT` handlers (`#1653`_).

.. _`#1631`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1631
.. _`#1506`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1506
.. _`#1558`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1558
.. _`#1569`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1569
.. _`#1579`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1579
.. _`#1572`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1572
.. _`#1566`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1566
.. _`#1577`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1577
.. _`#1533`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1533
.. _`#1560`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1560
.. _`#1574`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1574
.. _`#1555`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1555
.. _`#1556`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1556
.. _`#1605`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1605
.. _`#1606`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1606
.. _`#1607`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1607
.. _`#1612`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1612
.. _`#1615`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1615
.. _`#1618`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1618
.. _`#1600`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1600
.. _`#1619`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1619
.. _`#1653`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1653
.. _`#1656`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1656
.. _`#1645`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1645

Version 12.2.0
==============
*Released 2019-10-14*

**New features:**

- Nested ConversationHandlers (`#1512`_).

**Minor changes, CI improvments or bug fixes:**

- Fix CI failures due to non-backward compat attrs depndency (`#1540`_).
- travis.yaml: TEST_OFFICIAL removed from allowed_failures.
- Fix typos in examples (`#1537`_).
- Fix Bot.to_dict to use proper first_name (`#1525`_).
- Refactor ``test_commandhandler.py`` (`#1408`_).
- Add Python 3.8 (RC version) to Travis testing matrix (`#1543`_).
- test_bot.py: Add to_dict test (`#1544`_).
- Flake config moved into setup.cfg (`#1546`_).

.. _`#1512`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1512
.. _`#1540`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1540
.. _`#1537`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1537
.. _`#1525`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1525
.. _`#1408`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1408
.. _`#1543`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1543
.. _`#1544`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1544
.. _`#1546`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1546

Version 12.1.1
==============
*Released 2019-09-18*

**Hot fix release**

Fixed regression in the vendored urllib3 (`#1517`_).

.. _`#1517`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1517

Version 12.1.0
================
*Released 2019-09-13*

**Major changes:**

- Bot API 4.4 support (`#1464`_, `#1510`_)
- Add `get_file` method to `Animation` & `ChatPhoto`. Add, `get_small_file` & `get_big_file`
  methods to `ChatPhoto` (`#1489`_)
- Tools for deep linking (`#1049`_)

**Minor changes and/or bug fixes:**

- Documentation fixes (`#1500`_, `#1499`_)
- Improved examples (`#1502`_)

.. _`#1464`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1464
.. _`#1502`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1502
.. _`#1499`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1499
.. _`#1500`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1500
.. _`#1049`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1049
.. _`#1489`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1489
.. _`#1510`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1510

Version 12.0.0
================
*Released 2019-08-29*

Well... This felt like decades. But here we are with a new release.

Expect minor releases soon (mainly complete Bot API 4.4 support)

**Major and/or breaking changes:**

- Context based callbacks
- Persistence
- PrefixHandler added (Handler overhaul)
- Deprecation of RegexHandler and edited_messages, channel_post, etc. arguments (Filter overhaul)
- Various ConversationHandler changes and fixes
- Bot API 4.1, 4.2, 4.3 support
- Python 3.4 is no longer supported
- Error Handler now handles all types of exceptions (`#1485`_)
- Return UTC from from_timestamp() (`#1485`_)

**See the wiki page at https://git.io/fxJuV for a detailed guide on how to migrate from version 11 to version 12.**

Context based callbacks (`#1100`_)
----------------------------------

- Use of ``pass_`` in handlers is deprecated.
- Instead use ``use_context=True`` on ``Updater`` or ``Dispatcher`` and change callback from (bot, update, others...) to (update, context).
- This also applies to error handlers ``Dispatcher.add_error_handler`` and JobQueue jobs (change (bot, job) to (context) here).
- For users with custom handlers subclassing Handler, this is mostly backwards compatible, but to use the new context based callbacks you need to implement the new collect_additional_context method.
- Passing bot to ``JobQueue.__init__`` is deprecated. Use JobQueue.set_dispatcher with a dispatcher instead.
- Dispatcher makes sure to use a single `CallbackContext` for a entire update. This means that if an update is handled by multiple handlers (by using the group argument), you can add custom arguments to the `CallbackContext` in a lower group handler and use it in higher group handler. NOTE: Never use with @run_async, see docs for more info. (`#1283`_)
- If you have custom handlers they will need to be updated to support the changes in this release.
- Update all examples to use context based callbacks.

Persistence (`#1017`_)
----------------------

- Added PicklePersistence and DictPersistence for adding persistence to your bots.
- BasePersistence can be subclassed for all your persistence needs.
- Add a new example that shows a persistent ConversationHandler bot

Handler overhaul (`#1114`_)
---------------------------

- CommandHandler now only triggers on actual commands as defined by telegram servers (everything that the clients mark as a tabable link).
- PrefixHandler can be used if you need to trigger on prefixes (like all messages starting with a "/" (old CommandHandler behaviour) or even custom prefixes like "#" or "!").

Filter overhaul (`#1221`_)
--------------------------

- RegexHandler is deprecated and should be replaced with a MessageHandler with a regex filter.
- Use update filters to filter update types instead of arguments (message_updates, channel_post_updates and edited_updates) on the handlers.
- Completely remove allow_edited argument - it has been deprecated for a while.
- data_filters now exist which allows filters that return data into the callback function. This is how the regex filter is implemented.
- All this means that it no longer possible to use a list of filters in a handler. Use bitwise operators instead!

ConversationHandler
-------------------

- Remove ``run_async_timeout`` and ``timed_out_behavior`` arguments (`#1344`_)
- Replace with ``WAITING`` constant and behavior from states (`#1344`_)
- Only emit one warning for multiple CallbackQueryHandlers in a ConversationHandler (`#1319`_)
- Use warnings.warn for ConversationHandler warnings (`#1343`_)
- Fix unresolvable promises (`#1270`_)


Bug fixes & improvements
------------------------

- Handlers should be faster due to deduped logic.
- Avoid compiling compiled regex in regex filter. (`#1314`_)
- Add missing ``left_chat_member`` to Message.MESSAGE_TYPES (`#1336`_)
- Make custom timeouts actually work properly (`#1330`_)
- Add convenience classmethods (from_button, from_row and from_column) to InlineKeyboardMarkup
- Small typo fix in setup.py (`#1306`_)
- Add Conflict error (HTTP error code 409) (`#1154`_)
- Change MAX_CAPTION_LENGTH to 1024 (`#1262`_)
- Remove some unnecessary clauses (`#1247`_, `#1239`_)
- Allow filenames without dots in them when sending files (`#1228`_)
- Fix uploading files with unicode filenames (`#1214`_)
- Replace http.server with Tornado (`#1191`_)
- Allow SOCKSConnection to parse username and password from URL (`#1211`_)
- Fix for arguments in passport/data.py (`#1213`_)
- Improve message entity parsing by adding text_mention (`#1206`_)
- Documentation fixes (`#1348`_, `#1397`_, `#1436`_)
- Merged filters short-circuit (`#1350`_)
- Fix webhook listen with tornado (`#1383`_)
- Call task_done() on update queue after update processing finished (`#1428`_)
- Fix send_location() - latitude may be 0 (`#1437`_)
- Make MessageEntity objects comparable (`#1465`_)
- Add prefix to thread names (`#1358`_)

Buf fixes since v12.0.0b1
-------------------------

- Fix setting bot on ShippingQuery (`#1355`_)
- Fix _trigger_timeout() missing 1 required positional argument: 'job' (`#1367`_)
- Add missing message.text check in PrefixHandler check_update (`#1375`_)
- Make updates persist even on DispatcherHandlerStop (`#1463`_)
- Dispatcher force updating persistence object's chat data attribute(`#1462`_)

.. _`#1100`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1100
.. _`#1283`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1283
.. _`#1017`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1017
.. _`#1325`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1325
.. _`#1301`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1301
.. _`#1312`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1312
.. _`#1324`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1324
.. _`#1114`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1114
.. _`#1221`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1221
.. _`#1314`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1314
.. _`#1336`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1336
.. _`#1330`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1330
.. _`#1306`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1306
.. _`#1154`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1154
.. _`#1262`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1262
.. _`#1247`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1247
.. _`#1239`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1239
.. _`#1228`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1228
.. _`#1214`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1214
.. _`#1191`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1191
.. _`#1211`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1211
.. _`#1213`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1213
.. _`#1206`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1206
.. _`#1344`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1344
.. _`#1319`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1319
.. _`#1343`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1343
.. _`#1270`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1270
.. _`#1348`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1348
.. _`#1350`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1350
.. _`#1383`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1383
.. _`#1397`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1397
.. _`#1428`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1428
.. _`#1436`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1436
.. _`#1437`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1437
.. _`#1465`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1465
.. _`#1358`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1358
.. _`#1355`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1355
.. _`#1367`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1367
.. _`#1375`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1375
.. _`#1463`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1463
.. _`#1462`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1462
.. _`#1483`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1483
.. _`#1485`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1485

Internal improvements
---------------------

- Finally fix our CI builds mostly (too many commits and PRs to list)
- Use multiple bots for CI to improve testing times significantly.
- Allow pypy to fail in CI.
- Remove the last CamelCase CheckUpdate methods from the handlers we missed earlier.
- test_official is now executed in a different job

Version 11.1.0
==============
*Released 2018-09-01*

Fixes and updates for Telegram Passport: (`#1198`_)

- Fix passport decryption failing at random times
- Added support for middle names.
- Added support for translations for documents
- Add errors for translations for documents
- Added support for requesting names in the language of the user's country of residence
- Replaced the payload parameter with the new parameter nonce
- Add hash to EncryptedPassportElement

.. _`#1198`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1198

Version 11.0.0
==============
*Released 2018-08-29*

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

Version 10.1.0
==============
*Released 2018-05-02*

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

Version 10.0.2
==============
*Released 2018-04-17*

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

Version 10.0.1
==============
*Released 2018-03-05*

Fixes:

- Fix conversationhandler timeout (PR `#1032`_)
- Add missing docs utils (PR `#912`_)

.. _`#1032`: https://github.com/python-telegram-bot/python-telegram-bot/pull/826
.. _`#912`: https://github.com/python-telegram-bot/python-telegram-bot/pull/826

Version 10.0.0
==============
*Released 2018-03-02*

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

Version 9.0.0
=============
*Released 2017-12-08*

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

Version 8.1.1
=============
*Released 2017-10-15*

- Fix Commandhandler crashing on single character messages (PR `#873`_).

.. _`#873`: https://github.com/python-telegram-bot/python-telegram-bot/pull/871

Version 8.1.0
=============
*Released 2017-10-14*

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

Version 8.0.0
=============
*Released 2017-09-01*

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

Version 7.0.1
===============
*Released 2017-07-28*

- Fix TypeError exception in RegexHandler (PR #751).
- Small documentation fix (PR #749).

Version 7.0.0
=============
*Released 2017-07-25*

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

Pre-version 7.0
===============

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
