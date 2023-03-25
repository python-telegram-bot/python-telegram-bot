=========
Changelog
=========

Version 20.2
============
*Released 2023-03-25*

This is the technical changelog for version 20.2. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------
- Full Support for API 6.6 (`#3584`_)
- Revert to HTTP/1.1 as Default and make HTTP/2 an Optional Dependency (`#3576`_)

Minor Changes, Documentation Improvements and CI
------------------------------------------------
- Documentation Improvements (`#3565`_, `#3600`_)
- Handle Symbolic Links in ``was_called_by`` (`#3552`_)
- Tidy Up Tests Directory (`#3553`_)
- Enhance ``Application.create_task`` (`#3543`_)
- Make Type Completeness Workflow Usable for ``PRs`` from Forks (`#3551`_)
- Refactor and Overhaul the Test Suite (`#3426`_)

Dependencies
------------
- Bump ``pytest-asyncio`` from 0.20.3 to 0.21.0 (`#3624`_)
- Bump ``furo`` from 2022.12.7 to 2023.3.23 (`#3625`_)
- Bump ``pytest-xdist`` from 3.2.0 to 3.2.1 (`#3606`_)
- ``pre-commit`` autoupdate (`#3577`_)
- Update ``apscheduler`` requirement from ~=3.10.0 to ~=3.10.1 (`#3572`_)
- Bump ``pytest`` from 7.2.1 to 7.2.2 (`#3573`_)
- Bump ``pytest-xdist`` from 3.1.0 to 3.2.0 (`#3550`_)
- Bump ``sphinxcontrib-mermaid`` from 0.7.1 to 0.8 (`#3549`_)

.. _`#3584`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3584
.. _`#3576`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3576
.. _`#3565`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3565
.. _`#3600`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3600
.. _`#3552`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3552
.. _`#3553`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3553
.. _`#3543`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3543
.. _`#3551`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3551
.. _`#3426`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3426
.. _`#3624`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3624
.. _`#3625`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3625
.. _`#3606`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3606
.. _`#3577`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3577
.. _`#3572`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3572
.. _`#3573`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3573
.. _`#3550`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3550
.. _`#3549`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3549

Version 20.1
============
*Released 2023-02-09*

This is the technical changelog for version 20.1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support for Bot API 6.5 (`#3530`_)

New Features
------------

- Add ``Application(Builder).post_stop`` (`#3466`_)
- Add ``Chat.effective_name`` Convenience Property (`#3485`_)
- Allow to Adjust HTTP Version and Use HTTP/2 by Default (`#3506`_)

Documentation Improvements
--------------------------

- Enhance ``chatmemberbot`` Example (`#3500`_)
- Automatically Generate Cross-Reference Links (`#3501`_, `#3529`_, `#3523`_)
- Add Some Graphic Elements to Docs (`#3535`_)
- Various Smaller Improvements (`#3464`_, `#3483`_, `#3484`_, `#3497`_, `#3512`_, `#3515`_,  `#3498`_)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Update Copyright to 2023 (`#3459`_)
- Stabilize Tests on Closing and Hiding the General Forum Topic (`#3460`_)
- Fix Dependency Warning Typo (`#3474`_)
- Cache Dependencies on ``GitHub`` Actions (`#3469`_)
- Store Documentation Builts as ``GitHub`` Actions Artifacts (`#3468`_)
- Add ``ruff`` to ``pre-commit`` Hooks (`#3488`_)
- Improve Warning for ``days`` Parameter of  ``JobQueue.run_daily`` (`#3503`_)
- Improve Error Message for ``NetworkError`` (`#3505`_)
- Lock Inactive Threads Only Once Each Day (`#3510`_)
- Bump ``pytest`` from 7.2.0 to 7.2.1 (`#3513`_)
- Check for 3D Arrays in ``check_keyboard_type`` (`#3514`_)
- Explicit Type Annotations (`#3508`_)
- Increase Verbosity of Type Completeness CI Job (`#3531`_)
- Fix CI on Python 3.11 + Windows (`#3547`_)

Dependencies
------------

- Bump ``actions/stale`` from 6 to 7 (`#3461`_)
- Bump ``dessant/lock-threads`` from 3.0.0 to 4.0.0 (`#3462`_)
- ``pre-commit`` autoupdate (`#3470`_)
- Update ``httpx`` requirement from ~=0.23.1 to ~=0.23.3 (`#3489`_)
- Update ``cachetools`` requirement from ~=5.2.0 to ~=5.2.1 (`#3502`_)
- Improve Config for ``ruff`` and Bump to ``v0.0.222`` (`#3507`_)
- Update ``cachetools`` requirement from ~=5.2.1 to ~=5.3.0 (`#3520`_)
- Bump ``isort`` to 5.12.0 (`#3525`_)
- Update ``apscheduler`` requirement from ~=3.9.1 to ~=3.10.0 (`#3532`_)
- ``pre-commit`` autoupdate (`#3537`_)
- Update ``cryptography`` requirement to >=39.0.1 to address Vulnerability (`#3539`_)



.. _`#3530`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3530
.. _`#3466`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3466
.. _`#3485`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3485
.. _`#3506`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3506
.. _`#3500`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3500
.. _`#3501`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3501
.. _`#3529`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3529
.. _`#3523`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3523
.. _`#3535`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3535
.. _`#3464`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3464
.. _`#3483`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3483
.. _`#3484`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3484
.. _`#3497`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3497
.. _`#3512`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3512
.. _`#3515`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3515
.. _`#3498`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3498
.. _`#3459`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3459
.. _`#3460`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3460
.. _`#3474`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3474
.. _`#3469`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3469
.. _`#3468`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3468
.. _`#3488`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3488
.. _`#3503`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3503
.. _`#3505`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3505
.. _`#3510`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3510
.. _`#3513`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3513
.. _`#3514`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3514
.. _`#3508`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3508
.. _`#3531`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3531
.. _`#3547`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3547
.. _`#3461`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3461
.. _`#3462`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3462
.. _`#3470`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3470
.. _`#3489`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3489
.. _`#3502`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3502
.. _`#3507`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3507
.. _`#3520`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3520
.. _`#3525`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3525
.. _`#3532`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3532
.. _`#3537`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3537
.. _`#3539`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3539

Version 20.0
============
*Released 2023-01-01*

This is the technical changelog for version 20.0. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support For Bot API 6.4 (`#3449`_)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Documentation Improvements (`#3428`_, `#3423`_, `#3429`_, `#3441`_, `#3404`_, `#3443`_)
- Allow ``Sequence`` Input for Bot Methods (`#3412`_)
- Update Link-Check CI and Replace a Dead Link (`#3456`_)
- Freeze Classes Without Arguments (`#3453`_)
- Add New Constants (`#3444`_)
- Override ``Bot.__deepcopy__`` to Raise ``TypeError`` (`#3446`_)
- Add Log Decorator to ``Bot.get_webhook_info`` (`#3442`_)
- Add Documentation On Verifying Releases (`#3436`_)
- Drop Undocumented ``Job.__lt__`` (`#3432`_)

Dependencies
------------

- Downgrade ``sphinx`` to 5.3.0 to Fix Search (`#3457`_)
- Bump ``sphinx`` from 5.3.0 to 6.0.0 (`#3450`_)

.. _`#3449`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3449
.. _`#3428`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3428
.. _`#3423`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3423
.. _`#3429`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3429
.. _`#3441`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3441
.. _`#3404`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3404
.. _`#3443`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3443
.. _`#3412`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3412
.. _`#3456`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3456
.. _`#3453`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3453
.. _`#3444`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3444
.. _`#3446`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3446
.. _`#3442`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3442
.. _`#3436`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3436
.. _`#3432`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3432
.. _`#3457`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3457
.. _`#3450`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3450

Version 20.0b0
==============
*Released 2022-12-15*

This is the technical changelog for version 20.0b0. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Make ``TelegramObject`` Immutable (`#3249`_)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Reduce Code Duplication in Testing ``Defaults`` (`#3419`_)
- Add Notes and Warnings About Optional Dependencies (`#3393`_)
- Simplify Internals of ``Bot`` Methods (`#3396`_)
- Reduce Code Duplication in Several ``Bot`` Methods (`#3385`_)
- Documentation Improvements (`#3386`_, `#3395`_, `#3398`_, `#3403`_)

Dependencies
------------

- Bump ``pytest-xdist`` from 3.0.2 to 3.1.0 (`#3415`_)
- Bump ``pytest-asyncio`` from 0.20.2 to 0.20.3 (`#3417`_)
- ``pre-commit`` autoupdate (`#3409`_)

.. _`#3249`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3249
.. _`#3419`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3419
.. _`#3393`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3393
.. _`#3396`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3396
.. _`#3385`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3385
.. _`#3386`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3386
.. _`#3395`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3395
.. _`#3398`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3398
.. _`#3403`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3403
.. _`#3415`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3415
.. _`#3417`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3417
.. _`#3409`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3409

Version 20.0a6
==============
*Released 2022-11-24*

This is the technical changelog for version 20.0a6. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Bug Fixes
---------

- Only Persist Arbitrary ``callback_data`` if ``ExtBot.callback_data_cache`` is Present (`#3384`_)
- Improve Backwards Compatibility of ``TelegramObjects`` Pickle Behavior (`#3382`_)
- Fix Naming and Keyword Arguments of ``File.download_*`` Methods (`#3380`_)
- Fix Return Value Annotation of ``Chat.create_forum_topic`` (`#3381`_)

.. _`#3384`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3384
.. _`#3382`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3382
.. _`#3380`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3380
.. _`#3381`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3381

Version 20.0a5
==============
*Released 2022-11-22*

This is the technical changelog for version 20.0a5. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- API 6.3 (`#3346`_, `#3343`_, `#3342`_, `#3360`_)
- Explicit ``local_mode`` Setting (`#3154`_)
- Make Almost All 3rd Party Dependencies Optional (`#3267`_)
- Split ``File.download`` Into ``File.download_to_drive`` And ``File.download_to_memory`` (`#3223`_)

New Features
------------

- Add Properties for API Settings of ``Bot`` (`#3247`_)
- Add ``chat_id`` and ``username`` Parameters to ``ChatJoinRequestHandler`` (`#3261`_)
- Introduce ``TelegramObject.api_kwargs`` (`#3233`_)
- Add Two Constants Related to Local Bot API Servers (`#3296`_)
- Add ``recursive`` Parameter to ``TelegramObject.to_dict()`` (`#3276`_)
- Overhaul String Representation of ``TelegramObject`` (`#3234`_)
- Add Methods ``Chat.mention_{html, markdown, markdown_v2}`` (`#3308`_)
- Add ``constants.MessageLimit.DEEP_LINK_LENGTH`` (`#3315`_)
- Add Shortcut Parameters ``caption``, ``parse_mode`` and ``caption_entities`` to ``Bot.send_media_group`` (`#3295`_)
- Add Several New Enums To Constants (`#3351`_)

Bug Fixes
---------

- Fix ``CallbackQueryHandler`` Not Handling Non-String Data Correctly With Regex Patterns (`#3252`_)
- Fix Defaults Handling in ``Bot.answer_web_app_query`` (`#3362`_)

Documentation Improvements
--------------------------

- Update PR Template (`#3361`_)
- Document Dunder Methods of ``TelegramObject`` (`#3319`_)
- Add Several References to Wiki pages (`#3306`_)
- Overhaul Search bar (`#3218`_)
- Unify Documentation of Arguments and Attributes of Telegram Classes (`#3217`_, `#3292`_, `#3303`_, `#3312`_, `#3314`_)
- Several Smaller Improvements (`#3214`_, `#3271`_, `#3289`_, `#3326`_, `#3370`_, `#3376`_, `#3366`_)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Improve Warning About Unknown ``ConversationHandler`` States (`#3242`_)
- Switch from Stale Bot to ``GitHub`` Actions (`#3243`_)
- Bump Python 3.11 to RC2 in Test Matrix (`#3246`_)
- Make ``Job.job`` a Property and Make ``Jobs`` Hashable (`#3250`_)
- Skip ``JobQueue`` Tests on Windows Again (`#3280`_)
- Read-Only ``CallbackDataCache`` (`#3266`_)
- Type Hinting Fix for ``Message.effective_attachment`` (`#3294`_)
- Run Unit Tests in Parallel (`#3283`_)
- Update Test Matrix to Use Stable Python 3.11 (`#3313`_)
- Don't Edit Objects In-Place When Inserting ``ext.Defaults`` (`#3311`_)
- Add a Test for ``MessageAttachmentType`` (`#3335`_)
- Add Three New Test Bots (`#3347`_)
- Improve Unit Tests Regarding ``ChatMemberUpdated.difference`` (`#3352`_)
- Flaky Unit Tests: Use ``pytest`` Marker (`#3354`_)
- Fix ``DeepSource`` Issues (`#3357`_)
- Handle Lists and Tuples and Datetimes Directly in ``TelegramObject.to_dict`` (`#3353`_)
- Update Meta Config (`#3365`_)
- Merge ``ChatDescriptionLimit`` Enum Into ``ChatLimit`` (`#3377`_)

Dependencies
------------

- Bump ``pytest`` from 7.1.2 to 7.1.3 (`#3228`_)
- ``pre-commit`` Updates (`#3221`_)
- Bump ``sphinx`` from 5.1.1 to 5.2.3 (`#3269`_)
- Bump ``furo`` from 2022.6.21 to 2022.9.29 (`#3268`_)
- Bump ``actions/stale`` from 5 to 6 (`#3277`_)
- ``pre-commit`` autoupdate (`#3282`_)
- Bump ``sphinx`` from 5.2.3 to 5.3.0 (`#3300`_)
- Bump ``pytest-asyncio`` from 0.19.0 to 0.20.1 (`#3299`_)
- Bump ``pytest`` from 7.1.3 to 7.2.0 (`#3318`_)
- Bump ``pytest-xdist`` from 2.5.0 to 3.0.2 (`#3317`_)
- ``pre-commit`` autoupdate (`#3325`_)
- Bump ``pytest-asyncio`` from 0.20.1 to 0.20.2 (`#3359`_)
- Update ``httpx`` requirement from ~=0.23.0 to ~=0.23.1 (`#3373`_)

.. _`#3346`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3346
.. _`#3343`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3343
.. _`#3342`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3342
.. _`#3360`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3360
.. _`#3154`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3154
.. _`#3267`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3267
.. _`#3223`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3223
.. _`#3247`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3247
.. _`#3261`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3261
.. _`#3233`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3233
.. _`#3296`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3296
.. _`#3276`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3276
.. _`#3234`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3234
.. _`#3308`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3308
.. _`#3315`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3315
.. _`#3295`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3295
.. _`#3351`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3351
.. _`#3252`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3252
.. _`#3362`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3362
.. _`#3361`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3361
.. _`#3319`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3319
.. _`#3306`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3306
.. _`#3218`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3218
.. _`#3217`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3217
.. _`#3292`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3292
.. _`#3303`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3303
.. _`#3312`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3312
.. _`#3314`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3314
.. _`#3214`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3214
.. _`#3271`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3271
.. _`#3289`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3289
.. _`#3326`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3326
.. _`#3370`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3370
.. _`#3376`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3376
.. _`#3366`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3366
.. _`#3242`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3242
.. _`#3243`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3243
.. _`#3246`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3246
.. _`#3250`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3250
.. _`#3280`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3280
.. _`#3266`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3266
.. _`#3294`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3294
.. _`#3283`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3283
.. _`#3313`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3313
.. _`#3311`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3311
.. _`#3335`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3335
.. _`#3347`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3347
.. _`#3352`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3352
.. _`#3354`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3354
.. _`#3357`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3357
.. _`#3353`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3353
.. _`#3365`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3365
.. _`#3377`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3377
.. _`#3228`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3228
.. _`#3221`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3221
.. _`#3269`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3269
.. _`#3268`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3268
.. _`#3277`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3277
.. _`#3282`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3282
.. _`#3300`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3300
.. _`#3299`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3299
.. _`#3318`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3318
.. _`#3317`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3317
.. _`#3325`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3325
.. _`#3359`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3359
.. _`#3373`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3373

Version 20.0a4
==============
*Released 2022-08-27*

This is the technical changelog for version 20.0a4. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Hot Fixes
---------

* Fix a Bug in ``setup.py`` Regarding Optional Dependencies (`#3209`_)

.. _`#3209`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3209

Version 20.0a3
==============
*Released 2022-08-27*

This is the technical changelog for version 20.0a3. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support for API 6.2 (`#3195`_)

New Features
------------

- New Rate Limiting Mechanism (`#3148`_)
- Make ``chat/user_data`` Available in Error Handler for Errors in Jobs (`#3152`_)
- Add ``Application.post_shutdown`` (`#3126`_)

Bug Fixes
---------

- Fix ``helpers.mention_markdown`` for Markdown V1 and Improve Related Unit Tests (`#3155`_)
- Add ``api_kwargs`` Parameter to ``Bot.log_out`` and Improve Related Unit Tests (`#3147`_)
- Make ``Bot.delete_my_commands`` a Coroutine Function (`#3136`_)
- Fix ``ConversationHandler.check_update`` not respecting ``per_user`` (`#3128`_)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Add Python 3.11 to Test Suite & Adapt Enum Behaviour (`#3168`_)
- Drop Manual Token Validation (`#3167`_)
- Simplify Unit Tests for ``Bot.send_chat_action`` (`#3151`_)
- Drop ``pre-commit`` Dependencies from ``requirements-dev.txt`` (`#3120`_)
- Change Default Values for ``concurrent_updates`` and ``connection_pool_size`` (`#3127`_)
- Documentation Improvements (`#3139`_, `#3153`_, `#3135`_)
- Type Hinting Fixes (`#3202`_)

Dependencies
------------

- Bump ``sphinx`` from 5.0.2 to 5.1.1 (`#3177`_)
- Update ``pre-commit`` Dependencies (`#3085`_)
- Bump ``pytest-asyncio`` from 0.18.3 to 0.19.0 (`#3158`_)
- Update ``tornado`` requirement from ~=6.1 to ~=6.2 (`#3149`_)
- Bump ``black`` from 22.3.0 to 22.6.0 (`#3132`_)
- Bump ``actions/setup-python`` from 3 to 4 (`#3131`_)

.. _`#3195`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3195
.. _`#3148`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3148
.. _`#3152`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3152
.. _`#3126`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3126
.. _`#3155`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3155
.. _`#3147`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3147
.. _`#3136`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3136
.. _`#3128`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3128
.. _`#3168`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3168
.. _`#3167`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3167
.. _`#3151`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3151
.. _`#3120`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3120
.. _`#3127`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3127
.. _`#3139`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3139
.. _`#3153`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3153
.. _`#3135`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3135
.. _`#3202`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3202
.. _`#3177`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3177
.. _`#3085`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3085
.. _`#3158`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3158
.. _`#3149`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3149
.. _`#3132`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3132
.. _`#3131`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3131

Version 20.0a2
==============
*Released 2022-06-27*

This is the technical changelog for version 20.0a2. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support for API 6.1 (`#3112`_)

New Features
------------

- Add Additional Shortcut Methods to ``Chat`` (`#3115`_)
- Mermaid-based Example State Diagrams (`#3090`_)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Documentation Improvements (`#3103`_, `#3121`_, `#3098`_)
- Stabilize CI (`#3119`_)
- Bump ``pyupgrade`` from 2.32.1 to 2.34.0 (`#3096`_)
- Bump ``furo`` from 2022.6.4 to 2022.6.4.1 (`#3095`_)
- Bump ``mypy`` from 0.960 to 0.961 (`#3093`_)

.. _`#3112`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3112
.. _`#3115`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3115
.. _`#3090`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3090
.. _`#3103`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3103
.. _`#3121`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3121
.. _`#3098`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3098
.. _`#3119`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3119
.. _`#3096`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3096
.. _`#3095`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3095
.. _`#3093`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3093

Version 20.0a1
==============
*Released 2022-06-09*

This is the technical changelog for version 20.0a1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes:
--------------

- Drop Support for ``ujson`` and instead ``BaseRequest.parse_json_payload`` (`#3037`_, `#3072`_)
- Drop ``InputFile.is_image`` (`#3053`_)
- Drop Explicit Type conversions in ``__init__`` s (`#3056`_)
- Handle List-Valued Attributes More Consistently (`#3057`_)
- Split ``{Command, Prefix}Handler`` And Make Attributes Immutable (`#3045`_)
- Align Behavior Of ``JobQueue.run_daily`` With ``cron`` (`#3046`_)
- Make PTB Specific  Keyword-Only Arguments for PTB Specific in Bot methods (`#3035`_)
- Adjust Equality Comparisons to Fit Bot API 6.0 (`#3033`_)
- Add Tuple Based Version Info (`#3030`_)- Improve Type Annotations for ``CallbackContext`` and Move Default Type Alias to ``ContextTypes.DEFAULT_TYPE`` (`#3017`_, `#3023`_)
- Rename ``Job.context`` to ``Job.data`` (`#3028`_)
- Rename ``Handler`` to ``BaseHandler`` (`#3019`_)

New Features:
-------------

- Add ``Application.post_init`` (`#3078`_)
- Add Arguments ``chat/user_id`` to ``CallbackContext`` And Example On Custom Webhook Setups (`#3059`_)
- Add Convenience Property ``Message.id`` (`#3077`_)
- Add Example for ``WebApp`` (`#3052`_)
- Rename ``telegram.bot_api_version`` to ``telegram.__bot_api_version__`` (`#3030`_)

Bug Fixes:
----------

- Fix Non-Blocking Entry Point in ``ConversationHandler`` (`#3068`_)
- Escape Backslashes in ``escape_markdown``  (`#3055`_)

Dependencies:
-------------

- Update ``httpx`` requirement from ~=0.22.0 to ~=0.23.0 (`#3069`_)
- Update ``cachetools`` requirement from ~=5.0.0 to ~=5.2.0 (`#3058`_, `#3080`_)

Minor Changes, Documentation Improvements and CI:
-------------------------------------------------

- Move Examples To Documentation (`#3089`_)
- Documentation Improvements and Update Dependencies (`#3010`_, `#3007`_, `#3012`_, `#3067`_, `#3081`_, `#3082`_)
- Improve Some Unit Tests (`#3026`_)
- Update Code Quality dependencies (`#3070`_, `#3032`_,`#2998`_, `#2999`_)
- Don't Set Signal Handlers On Windows By Default (`#3065`_)
- Split ``{Command, Prefix}Handler`` And Make Attributes Immutable (`#3045`_)
- Apply ``isort`` and Update ``pre-commit.ci`` Configuration (`#3049`_)
- Adjust ``pre-commit`` Settings for ``isort`` (`#3043`_)
- Add Version Check to Examples (`#3036`_)
- Use ``Collection`` Instead of ``List`` and ``Tuple`` (`#3025`_)
- Remove Client-Side Parameter Validation (`#3024`_)
- Don't Pass Default Values of Optional Parameters to Telegram (`#2978`_)
- Stabilize ``Application.run_*`` on Python 3.7 (`#3009`_)
- Ignore Code Style Commits in ``git blame`` (`#3003`_)
- Adjust Tests to Changed API Behavior (`#3002`_)

.. _`#2978`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2978
.. _`#2998`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2998
.. _`#2999`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2999
.. _`#3002`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3002
.. _`#3003`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3003
.. _`#3007`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3007
.. _`#3009`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3009
.. _`#3010`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3010
.. _`#3012`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3012
.. _`#3017`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3017
.. _`#3019`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3019
.. _`#3023`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3023
.. _`#3024`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3024
.. _`#3025`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3025
.. _`#3026`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3026
.. _`#3028`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3028
.. _`#3030`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3030
.. _`#3032`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3032
.. _`#3033`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3033
.. _`#3035`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3035
.. _`#3036`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3036
.. _`#3037`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3037
.. _`#3043`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3043
.. _`#3045`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3045
.. _`#3046`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3046
.. _`#3049`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3049
.. _`#3052`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3052
.. _`#3053`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3053
.. _`#3055`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3055
.. _`#3056`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3056
.. _`#3057`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3057
.. _`#3058`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3058
.. _`#3059`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3059
.. _`#3065`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3065
.. _`#3067`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3067
.. _`#3068`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3068
.. _`#3069`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3069
.. _`#3070`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3070
.. _`#3072`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3072
.. _`#3077`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3077
.. _`#3078`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3078
.. _`#3080`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3080
.. _`#3081`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3081
.. _`#3082`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3082
.. _`#3089`: https://github.com/python-telegram-bot/python-telegram-bot/pull/3089

Version 20.0a0
==============
*Released 2022-05-06*

This is the technical changelog for version 20.0a0. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes:
--------------

-  Refactor Initialization of Persistence Classes
   (`#2604 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2604>`__)
-  Drop Non-``CallbackContext`` API
   (`#2617 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2617>`__)
-  Remove ``__dict__`` from ``__slots__`` and drop Python 3.6
   (`#2619 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2619>`__,
   `#2636 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2636>`__)
-  Move and Rename ``TelegramDecryptionError`` to
   ``telegram.error.PassportDecryptionError``
   (`#2621 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2621>`__)
-  Make ``BasePersistence`` Methods Abstract
   (`#2624 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2624>`__)
-  Remove ``day_is_strict`` argument of ``JobQueue.run_monthly``
   (`#2634 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2634>`__
   by `iota-008 <https://github.com/iota-008>`__)
-  Move ``Defaults`` to ``telegram.ext``
   (`#2648 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2648>`__)
-  Remove Deprecated Functionality
   (`#2644 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2644>`__,
   `#2740 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2740>`__,
   `#2745 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2745>`__)
-  Overhaul of Filters
   (`#2759 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2759>`__,
   `#2922 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2922>`__)
-  Switch to ``asyncio`` and Refactor PTBs Architecture
   (`#2731 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2731>`__)
-  Improve ``Job.__getattr__``
   (`#2832 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2832>`__)
-  Remove ``telegram.ReplyMarkup``
   (`#2870 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2870>`__)
-  Persistence of ``Bots``: Refactor Automatic Replacement and
   Integration with ``TelegramObject``
   (`#2893 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2893>`__)

New Features:
-------------

-  Introduce Builder Pattern
   (`#2646 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2646>`__)
-  Add ``Filters.update.edited``
   (`#2705 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2705>`__
   by `PhilippFr <https://github.com/PhilippFr>`__)
-  Introduce ``Enums`` for ``telegram.constants``
   (`#2708 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2708>`__)
-  Accept File Paths for ``private_key``
   (`#2724 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2724>`__)
-  Associate ``Jobs`` with ``chat/user_id``
   (`#2731 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2731>`__)
-  Convenience Functionality for ``ChatInviteLinks``
   (`#2782 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2782>`__)
-  Add ``Dispatcher.add_handlers``
   (`#2823 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2823>`__)
-  Improve Error Messages in ``CommandHandler.__init__``
   (`#2837 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2837>`__)
-  ``Defaults.protect_content``
   (`#2840 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2840>`__)
-  Add ``Dispatcher.migrate_chat_data``
   (`#2848 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2848>`__
   by `DonalDuck004 <https://github.com/DonalDuck004>`__)
-  Add Method ``drop_chat/user_data`` to ``Dispatcher`` and Persistence
   (`#2852 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2852>`__)
-  Add methods ``ChatPermissions.{all, no}_permissions`` (`#2948 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2948>`__)
-  Full Support for API 6.0
   (`#2956 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2956>`__)
-  Add Python 3.10 to Test Suite
   (`#2968 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2968>`__)

Bug Fixes & Minor Changes:
--------------------------

-  Improve Type Hinting for ``CallbackContext``
   (`#2587 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2587>`__
   by `revolter <https://github.com/revolter>`__)
-  Fix Signatures and Improve ``test_official``
   (`#2643 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2643>`__)
-  Refine ``Dispatcher.dispatch_error``
   (`#2660 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2660>`__)
-  Make ``InlineQuery.answer`` Raise ``ValueError``
   (`#2675 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2675>`__)
-  Improve Signature Inspection for Bot Methods
   (`#2686 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2686>`__)
-  Introduce ``TelegramObject.set/get_bot``
   (`#2712 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2712>`__
   by `zpavloudis <https://github.com/zpavloudis>`__)
-  Improve Subscription of ``TelegramObject``
   (`#2719 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2719>`__
   by `SimonDamberg <https://github.com/SimonDamberg>`__)
-  Use Enums for Dynamic Types & Rename Two Attributes in ``ChatMember``
   (`#2817 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2817>`__)
-  Return Plain Dicts from ``BasePersistence.get_*_data``
   (`#2873 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2873>`__)
-  Fix a Bug in ``ChatMemberUpdated.difference``
   (`#2947 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2947>`__)
-  Update Dependency Policy
   (`#2958 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2958>`__)

Internal Restructurings & Improvements:
---------------------------------------

-  Add User Friendly Type Check For Init Of
   ``{Inline, Reply}KeyboardMarkup``
   (`#2657 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2657>`__)
-  Warnings Overhaul
   (`#2662 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2662>`__)
-  Clear Up Import Policy
   (`#2671 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2671>`__)
-  Mark Internal Modules As Private
   (`#2687 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2687>`__
   by `kencx <https://github.com/kencx>`__)
-  Handle Filepaths via the ``pathlib`` Module
   (`#2688 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2688>`__
   by `eldbud <https://github.com/eldbud>`__)
-  Refactor MRO of ``InputMedia*`` and Some File-Like Classes
   (`#2717 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2717>`__
   by `eldbud <https://github.com/eldbud>`__)
-  Update Exceptions for Immutable Attributes
   (`#2749 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2749>`__)
-  Refactor Warnings in ``ConversationHandler``
   (`#2755 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2755>`__,
   `#2784 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2784>`__)
-  Use ``__all__`` Consistently
   (`#2805 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2805>`__)

CI, Code Quality & Test Suite Improvements:
-------------------------------------------

-  Add Custom ``pytest`` Marker to Ease Development
   (`#2628 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2628>`__)
-  Pass Failing Jobs to Error Handlers
   (`#2692 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2692>`__)
-  Update Notification Workflows
   (`#2695 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2695>`__)
-  Use Error Messages for ``pylint`` Instead of Codes
   (`#2700 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2700>`__
   by `Piraty <https://github.com/Piraty>`__)
-  Make Tests Agnostic of the CWD
   (`#2727 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2727>`__
   by `eldbud <https://github.com/eldbud>`__)
-  Update Code Quality Dependencies
   (`#2748 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2748>`__)
-  Improve Code Quality
   (`#2783 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2783>`__)
-  Update ``pre-commit`` Settings & Improve a Test
   (`#2796 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2796>`__)
-  Improve Code Quality & Test Suite
   (`#2843 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2843>`__)
-  Fix failing animation tests
   (`#2865 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2865>`__)
-  Update and Expand Tests & pre-commit Settings and Improve Code
   Quality
   (`#2925 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2925>`__)
-  Extend Code Formatting With Black
   (`#2972 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2972>`__)
-  Update Workflow Permissions
   (`#2984 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2984>`__)
-  Adapt Tests to Changed ``Bot.get_file`` Behavior
   (`#2995 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2995>`__)

Documentation Improvements:
---------------------------

-  Doc Fixes
   (`#2597 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2597>`__)
-  Add Code Comment Guidelines to Contribution Guide
   (`#2612 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2612>`__)
-  Add Cross-References to External Libraries & Other Documentation
   Improvements
   (`#2693 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2693>`__,
   `#2691 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2691>`__
   by `joesinghh <https://github.com/joesinghh>`__,
   `#2739 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2739>`__
   by `eldbud <https://github.com/eldbud>`__)
-  Use Furo Theme, Make Parameters Referenceable, Add Documentation
   Building to CI, Improve Links to Source Code & Other Improvements
   (`#2856 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2856>`__,
   `#2798 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2798>`__,
   `#2854 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2854>`__,
   `#2841 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2841>`__)
-  Documentation Fixes & Improvements
   (`#2822 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2822>`__)
-  Replace ``git.io`` Links
   (`#2872 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2872>`__
   by `murugu-21 <https://github.com/murugu-21>`__)
-  Overhaul Readmes, Update RTD Startpage & Other Improvements
   (`#2969 <https://github.com/python-telegram-bot/python-telegram-bot/pull/2969>`__)

Version 13.11
=============
*Released 2022-02-02*

This is the technical changelog for version 13.11. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full Support for Bot API 5.7 (`#2881`_)

.. _`#2881`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2881

Version 13.10
=============
*Released 2022-01-03*

This is the technical changelog for version 13.10. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full Support for API 5.6 (`#2835`_)

**Minor Changes & Doc fixes:**

- Update Copyright to 2022 (`#2836`_)
- Update Documentation of ``BotCommand`` (`#2820`_)

.. _`#2835`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2835
.. _`#2836`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2836
.. _`#2820`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2820

Version 13.9
============
*Released 2021-12-11*

This is the technical changelog for version 13.9. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full Support for Api 5.5 (`#2809`_)

**Minor Changes**

- Adjust Automated Locking of Inactive Issues (`#2775`_)

.. _`#2809`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2809
.. _`#2775`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2775

Version 13.8.1
==============
*Released 2021-11-08*

This is the technical changelog for version 13.8.1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Doc fixes:**

- Add ``ChatJoinRequest(Handler)`` to Docs (`#2771`_)

.. _`#2771`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2771

Version 13.8
============
*Released 2021-11-08*

This is the technical changelog for version 13.8. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full support for API 5.4 (`#2767`_)

**Minor changes, CI improvements, Doc fixes and Type hinting:**

- Create Issue Template Forms (`#2689`_)
- Fix ``camelCase`` Functions in ``ExtBot`` (`#2659`_)
- Fix Empty Captions not Being Passed by ``Bot.copy_message`` (`#2651`_)
- Fix Setting Thumbs When Uploading A Single File (`#2583`_)
- Fix Bug in ``BasePersistence.insert``/``replace_bot`` for Objects with ``__dict__`` not in ``__slots__`` (`#2603`_)

.. _`#2767`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2767
.. _`#2689`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2689
.. _`#2659`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2659
.. _`#2651`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2651
.. _`#2583`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2583
.. _`#2603`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2603

Version 13.7
============
*Released 2021-07-01*

This is the technical changelog for version 13.7. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full support for Bot API 5.3 (`#2572`_)

**Bug Fixes:**

- Fix Bug in ``BasePersistence.insert/replace_bot`` for Objects with ``__dict__`` in their slots (`#2561`_)
- Remove Incorrect Warning About ``Defaults`` and ``ExtBot`` (`#2553`_)

**Minor changes, CI improvements, Doc fixes and Type hinting:**

- Type Hinting Fixes (`#2552`_)
- Doc Fixes (`#2551`_)
- Improve Deprecation Warning for ``__slots__`` (`#2574`_)
- Stabilize CI (`#2575`_)
- Fix Coverage Configuration (`#2571`_)
- Better Exception-Handling for ``BasePersistence.replace/insert_bot`` (`#2564`_)
- Remove Deprecated ``pass_args`` from Deeplinking Example (`#2550`_)

.. _`#2572`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2572
.. _`#2561`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2561
.. _`#2553`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2553
.. _`#2552`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2552
.. _`#2551`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2551
.. _`#2574`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2574
.. _`#2575`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2575
.. _`#2571`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2571
.. _`#2564`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2564
.. _`#2550`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2550

Version 13.6
============
*Released 2021-06-06*

New Features:

- Arbitrary ``callback_data`` (`#1844`_)
- Add ``ContextTypes`` & ``BasePersistence.refresh_user/chat/bot_data`` (`#2262`_)
- Add ``Filters.attachment`` (`#2528`_)
- Add ``pattern`` Argument to ``ChosenInlineResultHandler`` (`#2517`_)

Major Changes:

- Add ``slots`` (`#2345`_)

Minor changes, CI improvements, Doc fixes and Type hinting:

- Doc Fixes (`#2495`_, `#2510`_)
- Add ``max_connections`` Parameter to ``Updater.start_webhook`` (`#2547`_)
- Fix for ``Promise.done_callback`` (`#2544`_)
- Improve Code Quality (`#2536`_, `#2454`_)
- Increase Test Coverage of ``CallbackQueryHandler`` (`#2520`_)
- Stabilize CI (`#2522`_, `#2537`_, `#2541`_)
- Fix ``send_phone_number_to_provider`` argument for ``Bot.send_invoice`` (`#2527`_)
- Handle Classes as Input for ``BasePersistence.replace/insert_bot`` (`#2523`_)
- Bump Tornado Version and Remove Workaround from `#2067`_ (`#2494`_)

.. _`#1844`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1844
.. _`#2262`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2262
.. _`#2528`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2528
.. _`#2517`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2517
.. _`#2345`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2345
.. _`#2495`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2495
.. _`#2547`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2547
.. _`#2544`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2544
.. _`#2536`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2536
.. _`#2454`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2454
.. _`#2520`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2520
.. _`#2522`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2522
.. _`#2537`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2537
.. _`#2541`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2541
.. _`#2527`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2527
.. _`#2523`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2523
.. _`#2067`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2067
.. _`#2494`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2494
.. _`#2510`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2510

Version 13.5
============
*Released 2021-04-30*

**Major Changes:**

- Full support of Bot API 5.2 (`#2489`_).

  .. note::
     The ``start_parameter`` argument of ``Bot.send_invoice`` and the corresponding shortcuts is now optional, so the order of
     parameters had to be changed. Make sure to update your method calls accordingly.

- Update ``ChatActions``, Deprecating ``ChatAction.RECORD_AUDIO`` and ``ChatAction.UPLOAD_AUDIO`` (`#2460`_)

**New Features:**

- Convenience Utilities & Example for Handling ``ChatMemberUpdated`` (`#2490`_)
- ``Filters.forwarded_from`` (`#2446`_)

**Minor changes, CI improvements, Doc fixes and Type hinting:**

- Improve Timeouts in ``ConversationHandler`` (`#2417`_)
- Stabilize CI (`#2480`_)
- Doc Fixes (`#2437`_)
- Improve Type Hints of Data Filters (`#2456`_)
- Add Two ``UserWarnings`` (`#2464`_)
- Improve Code Quality (`#2450`_)
- Update Fallback Test-Bots (`#2451`_)
- Improve Examples (`#2441`_, `#2448`_)

.. _`#2489`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2489
.. _`#2460`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2460
.. _`#2490`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2490
.. _`#2446`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2446
.. _`#2417`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2417
.. _`#2480`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2480
.. _`#2437`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2437
.. _`#2456`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2456
.. _`#2464`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2464
.. _`#2450`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2450
.. _`#2451`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2451
.. _`#2441`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2441
.. _`#2448`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2448

Version 13.4.1
==============
*Released 2021-03-14*

**Hot fix release:**

- Fixed a bug in ``setup.py`` (`#2431`_)

.. _`#2431`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2431

Version 13.4
============
*Released 2021-03-14*

**Major Changes:**

- Full support of Bot API 5.1 (`#2424`_)

**Minor changes, CI improvements, doc fixes and type hinting:**

- Improve ``Updater.set_webhook`` (`#2419`_)
- Doc Fixes (`#2404`_)
- Type Hinting Fixes (`#2425`_)
- Update ``pre-commit`` Settings (`#2415`_)
- Fix Logging for Vendored ``urllib3`` (`#2427`_)
- Stabilize Tests (`#2409`_)

.. _`#2424`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2424
.. _`#2419`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2419
.. _`#2404`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2404
.. _`#2425`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2425
.. _`#2415`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2415
.. _`#2427`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2427
.. _`#2409`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2409

Version 13.3
============
*Released 2021-02-19*

**Major Changes:**

- Make ``cryptography`` Dependency Optional & Refactor Some Tests (`#2386`_, `#2370`_)
- Deprecate ``MessageQueue`` (`#2393`_)

**Bug Fixes:**

- Refactor ``Defaults`` Integration (`#2363`_)
- Add Missing ``telegram.SecureValue`` to init and Docs (`#2398`_)

**Minor changes:**

- Doc Fixes (`#2359`_)

.. _`#2386`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2386
.. _`#2370`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2370
.. _`#2393`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2393
.. _`#2363`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2363
.. _`#2398`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2398
.. _`#2359`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2359

Version 13.2
============
*Released 2021-02-02*

**Major Changes:**

- Introduce ``python-telegram-bot-raw`` (`#2324`_)
- Explicit Signatures for Shortcuts (`#2240`_)

**New Features:**

- Add Missing Shortcuts to ``Message`` (`#2330`_)
- Rich Comparison for ``Bot`` (`#2320`_)
- Add ``run_async`` Parameter to ``ConversationHandler`` (`#2292`_)
- Add New Shortcuts to ``Chat`` (`#2291`_)
- Add New Constant ``MAX_ANSWER_CALLBACK_QUERY_TEXT_LENGTH`` (`#2282`_)
- Allow Passing Custom Filename For All Media (`#2249`_)
- Handle Bytes as File Input (`#2233`_)

**Bug Fixes:**

- Fix Escaping in Nested Entities in ``Message`` Properties (`#2312`_)
- Adjust Calling of ``Dispatcher.update_persistence`` (`#2285`_)
- Add ``quote`` kwarg to ``Message.reply_copy`` (`#2232`_)
- ``ConversationHandler``: Docs & ``edited_channel_post`` behavior (`#2339`_)

**Minor changes, CI improvements, doc fixes and type hinting:**

- Doc Fixes (`#2253`_, `#2225`_)
- Reduce Usage of ``typing.Any`` (`#2321`_)
- Extend Deeplinking Example (`#2335`_)
- Add pyupgrade to pre-commit Hooks (`#2301`_)
- Add PR Template (`#2299`_)
- Drop Nightly Tests & Update Badges (`#2323`_)
- Update Copyright (`#2289`_, `#2287`_)
- Change Order of Class DocStrings (`#2256`_)
- Add macOS to Test Matrix (`#2266`_)
- Start Using Versioning Directives in Docs (`#2252`_)
- Improve Annotations & Docs of Handlers (`#2243`_)

.. _`#2324`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2324
.. _`#2240`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2240
.. _`#2330`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2330
.. _`#2320`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2320
.. _`#2292`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2292
.. _`#2291`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2291
.. _`#2282`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2282
.. _`#2249`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2249
.. _`#2233`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2233
.. _`#2312`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2312
.. _`#2285`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2285
.. _`#2232`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2232
.. _`#2339`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2339
.. _`#2253`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2253
.. _`#2225`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2225
.. _`#2321`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2321
.. _`#2335`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2335
.. _`#2301`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2301
.. _`#2299`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2299
.. _`#2323`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2323
.. _`#2289`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2289
.. _`#2287`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2287
.. _`#2256`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2256
.. _`#2266`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2266
.. _`#2252`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2252
.. _`#2243`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2243

Version 13.1
============
*Released 2020-11-29*

**Major Changes:**

- Full support of Bot API 5.0 (`#2181`_, `#2186`_, `#2190`_, `#2189`_, `#2183`_, `#2184`_, `#2188`_, `#2185`_, `#2192`_, `#2196`_, `#2193`_, `#2223`_, `#2199`_, `#2187`_, `#2147`_, `#2205`_)

**New Features:**

- Add ``Defaults.run_async`` (`#2210`_)
- Improve and Expand ``CallbackQuery`` Shortcuts (`#2172`_)
- Add XOR Filters and make ``Filters.name`` a Property (`#2179`_)
- Add ``Filters.document.file_extension`` (`#2169`_)
- Add ``Filters.caption_regex`` (`#2163`_)
- Add ``Filters.chat_type`` (`#2128`_)
- Handle Non-Binary File Input (`#2202`_)

**Bug Fixes:**

- Improve Handling of Custom Objects in ``BasePersistence.insert``/``replace_bot`` (`#2151`_)
- Fix bugs in ``replace/insert_bot`` (`#2218`_)

**Minor changes, CI improvements, doc fixes and type hinting:**

- Improve Type hinting (`#2204`_, `#2118`_, `#2167`_, `#2136`_)
- Doc Fixes & Extensions (`#2201`_, `#2161`_)
- Use F-Strings Where Possible (`#2222`_)
- Rename kwargs to _kwargs where possible (`#2182`_)
- Comply with PEP561 (`#2168`_)
- Improve Code Quality (`#2131`_)
- Switch Code Formatting to Black (`#2122`_, `#2159`_, `#2158`_)
- Update Wheel Settings (`#2142`_)
- Update ``timerbot.py`` to ``v13.0`` (`#2149`_)
- Overhaul Constants (`#2137`_)
- Add Python 3.9 to Test Matrix (`#2132`_)
- Switch Codecov to ``GitHub`` Action (`#2127`_)
- Specify Required pytz Version (`#2121`_)


.. _`#2181`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2181
.. _`#2186`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2186
.. _`#2190`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2190
.. _`#2189`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2189
.. _`#2183`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2183
.. _`#2184`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2184
.. _`#2188`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2188
.. _`#2185`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2185
.. _`#2192`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2192
.. _`#2196`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2196
.. _`#2193`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2193
.. _`#2223`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2223
.. _`#2199`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2199
.. _`#2187`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2187
.. _`#2147`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2147
.. _`#2205`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2205
.. _`#2210`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2210
.. _`#2172`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2172
.. _`#2179`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2179
.. _`#2169`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2169
.. _`#2163`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2163
.. _`#2128`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2128
.. _`#2202`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2202
.. _`#2151`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2151
.. _`#2218`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2218
.. _`#2204`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2204
.. _`#2118`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2118
.. _`#2167`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2167
.. _`#2136`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2136
.. _`#2201`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2201
.. _`#2161`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2161
.. _`#2222`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2222
.. _`#2182`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2182
.. _`#2168`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2168
.. _`#2131`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2131
.. _`#2122`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2122
.. _`#2159`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2159
.. _`#2158`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2158
.. _`#2142`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2142
.. _`#2149`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2149
.. _`#2137`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2137
.. _`#2132`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2132
.. _`#2127`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2127
.. _`#2121`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2121

Version 13.0
============
*Released 2020-10-07*

**For a detailed guide on how to migrate from v12 to v13, see this** `wiki page <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-13.0>`_.

**Major Changes:**

- Deprecate old-style callbacks, i.e. set ``use_context=True`` by default (`#2050`_)
- Refactor Handling of Message VS Update Filters (`#2032`_)
- Deprecate ``Message.default_quote`` (`#1965`_)
- Refactor persistence of Bot instances (`#1994`_)
- Refactor ``JobQueue`` (`#1981`_)
- Refactor handling of kwargs in Bot methods (`#1924`_)
- Refactor ``Dispatcher.run_async``, deprecating the ``@run_async`` decorator (`#2051`_)

**New Features:**

- Type Hinting (`#1920`_)
- Automatic Pagination for ``answer_inline_query`` (`#2072`_)
- ``Defaults.tzinfo`` (`#2042`_)
- Extend rich comparison of objects (`#1724`_)
- Add ``Filters.via_bot`` (`#2009`_)
- Add missing shortcuts (`#2043`_)
- Allow ``DispatcherHandlerStop`` in ``ConversationHandler`` (`#2059`_)
- Make Errors picklable (`#2106`_)

**Minor changes, CI improvements, doc fixes or bug fixes:**

- Fix Webhook not working on Windows with Python 3.8+ (`#2067`_)
- Fix setting thumbs with ``send_media_group`` (`#2093`_)
- Make ``MessageHandler`` filter for ``Filters.update`` first (`#2085`_)
- Fix ``PicklePersistence.flush()`` with only ``bot_data`` (`#2017`_)
- Add test for clean argument of ``Updater.start_polling/webhook`` (`#2002`_)
- Doc fixes, refinements and additions (`#2005`_, `#2008`_, `#2089`_, `#2094`_, `#2090`_)
- CI fixes (`#2018`_, `#2061`_)
- Refine ``pollbot.py`` example (`#2047`_)
- Refine Filters in examples (`#2027`_)
- Rename ``echobot`` examples (`#2025`_)
- Use Lock-Bot to lock old threads (`#2048`_, `#2052`_, `#2049`_, `#2053`_)

.. _`#2050`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2050
.. _`#2032`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2032
.. _`#1965`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1965
.. _`#1994`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1994
.. _`#1981`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1981
.. _`#1924`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1924
.. _`#2051`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2051
.. _`#1920`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1920
.. _`#2072`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2072
.. _`#2042`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2042
.. _`#1724`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1724
.. _`#2009`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2009
.. _`#2043`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2043
.. _`#2059`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2059
.. _`#2106`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2106
.. _`#2067`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2067
.. _`#2093`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2093
.. _`#2085`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2085
.. _`#2017`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2017
.. _`#2002`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2002
.. _`#2005`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2005
.. _`#2008`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2008
.. _`#2089`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2089
.. _`#2094`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2094
.. _`#2090`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2090
.. _`#2018`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2018
.. _`#2061`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2061
.. _`#2047`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2047
.. _`#2027`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2027
.. _`#2025`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2025
.. _`#2048`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2048
.. _`#2052`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2052
.. _`#2049`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2049
.. _`#2053`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2053

Version 12.8
============
*Released 2020-06-22*

**Major Changes:**

- Remove Python 2 support (`#1715`_)
- Bot API 4.9 support (`#1980`_)
- IDs/Usernames of ``Filters.user`` and ``Filters.chat`` can now be updated (`#1757`_)

**Minor changes, CI improvements, doc fixes or bug fixes:**

- Update contribution guide and stale bot (`#1937`_)
- Remove ``NullHandlers`` (`#1913`_)
- Improve and expand examples (`#1943`_, `#1995`_, `#1983`_, `#1997`_)
- Doc fixes (`#1940`_, `#1962`_)
- Add ``User.send_poll()`` shortcut (`#1968`_)
- Ignore private attributes en ``TelegramObject.to_dict()`` (`#1989`_)
- Stabilize CI (`#2000`_)

.. _`#1937`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1937
.. _`#1913`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1913
.. _`#1943`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1943
.. _`#1757`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1757
.. _`#1940`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1940
.. _`#1962`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1962
.. _`#1968`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1968
.. _`#1989`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1989
.. _`#1995`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1995
.. _`#1983`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1983
.. _`#1715`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1715
.. _`#2000`: https://github.com/python-telegram-bot/python-telegram-bot/pull/2000
.. _`#1997`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1997
.. _`#1980`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1980

Version 12.7
============
*Released 2020-05-02*

**Major Changes:**

- Bot API 4.8 support. **Note:** The ``Dice`` object now has a second positional argument ``emoji``. This is relevant, if you instantiate ``Dice`` objects manually. (`#1917`_)
- Added ``tzinfo`` argument to ``helpers.from_timestamp``. It now returns an timezone aware object. This is relevant for ``Message.{date,forward_date,edit_date}``, ``Poll.close_date`` and ``ChatMember.until_date`` (`#1621`_)

**New Features:**

- New method ``run_monthly`` for the ``JobQueue`` (`#1705`_)
- ``Job.next_t`` now gives the datetime of the jobs next execution (`#1685`_)

**Minor changes, CI improvements, doc fixes or bug fixes:**

- Stabalize CI (`#1919`_, `#1931`_)
- Use ABCs ``@abstractmethod`` instead of raising ``NotImplementedError`` for ``Handler``, ``BasePersistence`` and ``BaseFilter`` (`#1905`_)
- Doc fixes (`#1914`_, `#1902`_, `#1910`_)

.. _`#1902`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1902
.. _`#1685`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1685
.. _`#1910`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1910
.. _`#1914`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1914
.. _`#1931`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1931
.. _`#1905`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1905
.. _`#1919`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1919
.. _`#1621`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1621
.. _`#1705`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1705
.. _`#1917`: https://github.com/python-telegram-bot/python-telegram-bot/pull/1917

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

**See the wiki page at https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-12.0 for a detailed guide on how to migrate from version 11 to version 12.**

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
.. _`our telegram passport wiki page`: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Telegram-Passport

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


.. _`see docs`: https://docs.python-telegram-bot.org/en/v13.11/telegram.ext.dispatcher.html?highlight=Dispatcher.add_handler#telegram.ext.Dispatcher.add_handler
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
- Please read the `Transistion Guide to 4.0 <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-4.0>`_

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
