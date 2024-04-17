.. _ptb-changelog:

=========
Changelog
=========

Version 21.1.1
==============

*Released 2024-04-15*

This is the technical changelog for version 21.1.1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Bug Fixes
---------

-  Fix Bug With Parameter ``message_thread_id`` of ``Message.reply_*`` (:pr:`4207` closes :issue:`4205`)

Minor Changes
-------------

-  Remove Deprecation Warning in ``JobQueue.run_daily`` (:pr:`4206` by `@Konano <https://github.com/Konano>`__)
-  Fix Annotation of ``EncryptedCredentials.decrypted_secret`` (:pr:`4199` by `@marinelay <https://github.com/marinelay>`__ closes :issue:`4198`)


Version 21.1
==============

*Released 2024-04-12*

This is the technical changelog for version 21.1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Major Changes
-------------

-  API 7.2 (:pr:`4180` closes :issue:`4179` and :issue:`4181`, :issue:`4181`)
-  Make ``ChatAdministratorRights/ChatMemberAdministrator.can_*_stories`` Required (API 7.1) (:pr:`4192`)

Minor Changes
-------------

-  Refactor Debug logging in ``Bot`` to Improve Type Hinting (:pr:`4151` closes :issue:`4010`)

New Features
------------

-  Make ``Message.reply_*`` Reply in the Same Topic by Default (:pr:`4170` by `@aelkheir <https://github.com/aelkheir>`__ closes :issue:`4139`)
-  Accept Socket Objects for Webhooks (:pr:`4161` closes :issue:`4078`)
-  Add ``Update.effective_sender`` (:pr:`4168` by `@aelkheir <https://github.com/aelkheir>`__ closes :issue:`4085`)

Documentation Improvements
--------------------------

-  Documentation Improvements (:pr:`4171`, :pr:`4158` by `@teslaedison <https://github.com/teslaedison>`__)

Internal Changes
----------------

-  Temporarily Mark Tests with ``get_sticker_set`` as XFAIL due to API 7.2 Update (:pr:`4190`)

Dependency Updates
------------------

-  ``pre-commit`` autoupdate (:pr:`4184`)
-  Bump ``dependabot/fetch-metadata`` from 1.6.0 to 2.0.0 (:pr:`4185`)


Version 21.0.1
==============

*Released 2024-03-06*

This is the technical changelog for version 21.0.1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Bug Fixes
---------

-  Remove ``docs`` from Package (:pr:`4150`)


Version 21.0
============

*Released 2024-03-06*

This is the technical changelog for version 21.0. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Major Changes
-------------

-  Remove Functionality Deprecated in API 7.0 (:pr:`4114` closes :issue:`4099`)
-  API 7.1 (:pr:`4118`)

New Features
------------

-  Add Parameter ``media_write_timeout`` to ``HTTPXRequest`` and Method ``ApplicationBuilder.media_write_timeout`` (:pr:`4120` closes :issue:`3864`)
-  Handle Properties in ``TelegramObject.__setstate__`` (:pr:`4134` closes :issue:`4111`)

Bug Fixes
---------

-  Add Missing Slot to ``Updater`` (:pr:`4130` closes :issue:`4127`)

Documentation Improvements
--------------------------

-  Improve HTML Download of Documentation (:pr:`4146` closes :issue:`4050`)
-  Documentation Improvements (:pr:`4109`, :issue:`4116`)
-  Update Copyright to 2024 (:pr:`4121` by `@aelkheir <https://github.com/aelkheir>`__ closes :issue:`4041`)

Internal Changes
----------------

-  Apply ``pre-commit`` Checks More Widely (:pr:`4135`)
-  Refactor and Overhaul ``test_official`` (:pr:`4087` closes :issue:`3874`)
-  Run Unit Tests in PRs on Requirements Changes (:pr:`4144`)
-  Make ``Updater.stop`` Independent of ``CancelledError`` (:pr:`4126`)

Dependency Updates
------------------

-  Relax Upper Bound for ``httpx`` Dependency (:pr:`4148`)
-  Bump ``test-summary/action`` from 2.2 to 2.3 (:pr:`4142`)
-  Update ``cachetools`` requirement from ~=5.3.2 to ~=5.3.3 (:pr:`4141`)
-  Update ``httpx`` requirement from ~=0.26.0 to ~=0.27.0 (:pr:`4131`)


Version 20.8
============

*Released 2024-02-08*

This is the technical changelog for version 20.8. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Major Changes
-------------

-  API 7.0 (:pr:`4034` closes :issue:`4033`, :pr:`4038` by `@aelkheir <https://github.com/aelkheir>`__)

Minor Changes
-------------

-  Fix Type Hint for ``filters`` Parameter of ``MessageHandler`` (:pr:`4039` by `@Palaptin <https://github.com/Palaptin>`__)
-  Deprecate ``filters.CHAT`` (:pr:`4083` closes :issue:`4062`)
-  Improve Error Handling in Built-In Webhook Handler (:pr:`3987` closes :issue:`3979`)

New Features
------------

-  Add Parameter ``pattern`` to ``PreCheckoutQueryHandler`` and ``filters.SuccessfulPayment`` (:pr:`4005` by `@aelkheir <https://github.com/aelkheir>`__ closes :issue:`3752`)
-  Add Missing Conversions of ``type`` to Corresponding Enum from ``telegram.constants`` (:pr:`4067`)
-  Add Support for Unix Sockets to ``Updater.start_webhook`` (:pr:`3986` closes :issue:`3978`)
-  Add ``Bot.do_api_request`` (:pr:`4084` closes :issue:`4053`)
-  Add ``AsyncContextManager`` as Parent Class to ``BaseUpdateProcessor`` (:pr:`4001`)

Documentation Improvements
--------------------------

-  Documentation Improvements (:pr:`3919`)
-  Add Docstring to Dunder Methods (:pr:`3929` closes :issue:`3926`)
-  Documentation Improvements (:pr:`4002`, :pr:`4079` by `@kenjitagawa <https://github.com/kenjitagawa>`__, :pr:`4104` by `@xTudoS <https://github.com/xTudoS>`__)

Internal Changes
----------------

-  Drop Usage of DeepSource (:pr:`4100`)
-  Improve Type Completeness & Corresponding Workflow (:pr:`4035`)
-  Bump ``ruff`` and Remove ``sort-all`` (:pr:`4075`)
-  Move Handler Files to ``_handlers`` Subdirectory (:pr:`4064` by `@lucasmolinari <https://github.com/lucasmolinari>`__ closes :issue:`4060`)
-  Introduce ``sort-all`` Hook for ``pre-commit`` (:pr:`4052`)
-  Use Recommended ``pre-commit`` Mirror for ``black`` (:pr:`4051`)
-  Remove Unused ``DEFAULT_20`` (:pr:`3997`)
-  Migrate From ``setup.cfg`` to ``pyproject.toml`` Where Possible (:pr:`4088`)

Dependency Updates
------------------

-  Bump ``black`` and ``ruff`` (:pr:`4089`)
-  Bump ``srvaroa/labeler`` from 1.8.0 to 1.10.0 (:pr:`4048`)
-  Update ``tornado`` requirement from ~=6.3.3 to ~=6.4 (:pr:`3992`)
-  Bump ``actions/stale`` from 8 to 9 (:pr:`4046`)
-  Bump ``actions/setup-python`` from 4 to 5 (:pr:`4047`)
-  ``pre-commit`` autoupdate (:pr:`4101`)
-  Bump ``actions/upload-artifact`` from 3 to 4 (:pr:`4045`)
-  ``pre-commit`` autoupdate (:pr:`3996`)
-  Bump ``furo`` from 2023.9.10 to 2024.1.29 (:pr:`4094`)
-  ``pre-commit`` autoupdate (:pr:`4043`)
-  Bump ``codecov/codecov-action`` from 3 to 4 (:pr:`4091`)
-  Bump ``EndBug/add-and-commit`` from 9.1.3 to 9.1.4 (:pr:`4090`)
-  Update ``httpx`` requirement from ~=0.25.2 to ~=0.26.0 (:pr:`4024`)
-  Bump ``pytest`` from 7.4.3 to 7.4.4 (:pr:`4056`)
-  Bump ``srvaroa/labeler`` from 1.7.0 to 1.8.0 (:pr:`3993`)
-  Bump ``test-summary/action`` from 2.1 to 2.2 (:pr:`4044`)
-  Bump ``dessant/lock-threads`` from 4.0.1 to 5.0.1 (:pr:`3994`)


Version 20.7
============

*Released 2023-11-27*

This is the technical changelog for version 20.7. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

New Features
------------

-  Add ``JobQueue.scheduler_configuration`` and Corresponding Warnings (:pr:`3913` closes :issue:`3837`)
-  Add Parameter ``socket_options`` to ``HTTPXRequest`` (:pr:`3935` closes :issue:`2965`)
-  Add ``ApplicationBuilder.(get_updates_)socket_options`` (:pr:`3943`)
-  Improve ``write_timeout`` Handling for Media Methods (:pr:`3952`)
-  Add ``filters.Mention`` (:pr:`3941` closes :issue:`3799`)
-  Rename ``proxy_url`` to ``proxy`` and Allow ``httpx.{Proxy, URL}`` as Input (:pr:`3939` closes :issue:`3844`)

Bug Fixes & Changes
-------------------

-  Adjust ``read_timeout`` Behavior for ``Bot.get_updates`` (:pr:`3963` closes :issue:`3893`)
-  Improve ``BaseHandler.__repr__`` for Callbacks without ``__qualname__`` (:pr:`3934`)
-  Fix Persistency Issue with Ended Non-Blocking Conversations (:pr:`3962`)
-  Improve Type Hinting for Arguments with Default Values in ``Bot`` (:pr:`3942`)

Documentation Improvements
--------------------------

-  Add Documentation for ``__aenter__`` and ``__aexit__`` Methods (:pr:`3907` closes :issue:`3886`)
-  Improve Insertion of Kwargs into ``Bot`` Methods (:pr:`3965`)

Internal Changes
----------------

-  Adjust Tests to New Error Messages (:pr:`3970`)

Dependency Updates
------------------

-  Bump ``pytest-xdist`` from 3.3.1 to 3.4.0 (:pr:`3975`)
-  ``pre-commit`` autoupdate (:pr:`3967`)
-  Update ``httpx`` requirement from ~=0.25.1 to ~=0.25.2 (:pr:`3983`)
-  Bump ``pytest-xdist`` from 3.4.0 to 3.5.0 (:pr:`3982`)
-  Update ``httpx`` requirement from ~=0.25.0 to ~=0.25.1 (:pr:`3961`)
-  Bump ``srvaroa/labeler`` from 1.6.1 to 1.7.0 (:pr:`3958`)
-  Update ``cachetools`` requirement from ~=5.3.1 to ~=5.3.2 (:pr:`3954`)
-  Bump ``pytest`` from 7.4.2 to 7.4.3 (:pr:`3953`)


Version 20.6
============

*Released 2023-10-03*

This is the technical changelog for version 20.6. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Major Changes
-------------

-  Drop Backward Compatibility Layer Introduced in :pr:`3853` (API 6.8) (:pr:`3873`)
-  Full Support for Bot API 6.9 (:pr:`3898`)

New Features
------------

-  Add Rich Equality Comparison to ``WriteAccessAllowed`` (:pr:`3911` closes :issue:`3909`)
-  Add ``__repr__`` Methods Added in :pr:`3826` closes :issue:`3770` to Sphinx Documentation (:pr:`3901` closes :issue:`3889`)
-  Add String Representation for Selected Classes (:pr:`3826` closes :issue:`3770`)

Minor Changes
-------------

-  Add Support Python 3.12 (:pr:`3915`)
-  Documentation Improvements (:pr:`3910`)

Internal Changes
----------------

-  Verify Type Hints for Bot Method & Telegram Class Parameters (:pr:`3868`)
-  Move Bot API Tests to Separate Workflow File (:pr:`3912`)
-  Fix Failing ``file_size`` Tests (:pr:`3906`)
-  Set Threshold for DeepSource’s PY-R1000 to High (:pr:`3888`)
-  One-Time Code Formatting Improvement via ``--preview`` Flag of ``black`` (:pr:`3882`)
-  Move Dunder Methods to the Top of Class Bodies (:pr:`3883`)
-  Remove Superfluous ``Defaults.__ne__`` (:pr:`3884`)

Dependency Updates
------------------

-  ``pre-commit`` autoupdate (:pr:`3876`)
-  Update ``pre-commit`` Dependencies (:pr:`3916`)
-  Bump ``actions/checkout`` from 3 to 4 (:pr:`3914`)
-  Update ``httpx`` requirement from ~=0.24.1 to ~=0.25.0 (:pr:`3891`)
-  Bump ``furo`` from 2023.8.19 to 2023.9.10 (:pr:`3890`)
-  Bump ``sphinx`` from 7.2.5 to 7.2.6 (:pr:`3892`)
-  Update ``tornado`` requirement from ~=6.2 to ~=6.3.3 (:pr:`3675`)
-  Bump ``pytest`` from 7.4.0 to 7.4.2 (:pr:`3881`)


Version 20.5
============
*Released 2023-09-03*

This is the technical changelog for version 20.5. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Major Changes
-------------

-  API 6.8 (:pr:`3853`)
-  Remove Functionality Deprecated Since Bot API 6.5, 6.6 or 6.7 (:pr:`3858`)

New Features
------------

-  Extend Allowed Values for HTTP Version (:pr:`3823` closes :issue:`3821`)
-  Add ``has_args`` Parameter to ``CommandHandler`` (:pr:`3854` by `@thatguylah <https://github.com/thatguylah>`__ closes :issue:`3798`)
-  Add ``Application.stop_running()`` and Improve Marking Updates as Read on ``Updater.stop()`` (:pr:`3804`)

Minor Changes
-------------

-  Type Hinting Fixes for ``WebhookInfo`` (:pr:`3871`)
-  Test and Document ``Exception.__cause__`` on ``NetworkError`` (:pr:`3792` closes :issue:`3778`)
-  Add Support for Python 3.12 RC (:pr:`3847`)

Documentation Improvements
--------------------------

-  Remove Version Check from Examples (:pr:`3846`)
-  Documentation Improvements (:pr:`3803`, :pr:`3797`, :pr:`3816` by `@trim21 <https://github.com/trim21>`__, :pr:`3829` by `@aelkheir <https://github.com/aelkheir>`__)
-  Provide Versions of ``customwebhookbot.py`` with Different Frameworks (:pr:`3820` closes :issue:`3717`)

Dependency Updates
------------------

-  ``pre-commit`` autoupdate (:pr:`3824`)
-  Bump ``srvaroa/labeler`` from 1.6.0 to 1.6.1 (:pr:`3870`)
-  Bump ``sphinx`` from 7.0.1 to 7.1.1 (:pr:`3818`)
-  Bump ``sphinx`` from 7.2.3 to 7.2.5 (:pr:`3869`)
-  Bump ``furo`` from 2023.5.20 to 2023.7.26 (:pr:`3817`)
-  Update ``apscheduler`` requirement from ~=3.10.3 to ~=3.10.4 (:pr:`3862`)
-  Bump ``sphinx`` from 7.2.2 to 7.2.3 (:pr:`3861`)
-  Bump ``pytest-asyncio`` from 0.21.0 to 0.21.1 (:pr:`3801`)
-  Bump ``sphinx-paramlinks`` from 0.5.4 to 0.6.0 (:pr:`3840`)
-  Update ``apscheduler`` requirement from ~=3.10.1 to ~=3.10.3 (:pr:`3851`)
-  Bump ``furo`` from 2023.7.26 to 2023.8.19 (:pr:`3850`)
-  Bump ``sphinx`` from 7.1.2 to 7.2.2 (:pr:`3852`)
-  Bump ``sphinx`` from 7.1.1 to 7.1.2 (:pr:`3827`)


Version 20.4
============

*Released 2023-07-09*

This is the technical changelog for version 20.4. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`__.

Major Changes
-------------

-  Drop Support for Python 3.7 (:pr:`3728`, :pr:`3742` by `@Trifase <https://github.com/Trifase>`__, :pr:`3749` by `@thefunkycat <https://github.com/thefunkycat>`__, :pr:`3740` closes :issue:`3732`, :pr:`3754` closes :issue:`3731`, :pr:`3753`, :pr:`3764`, :pr:`3762`, :pr:`3759` closes :issue:`3733`)

New Features
------------

-  Make Integration of ``APScheduler`` into ``JobQueue`` More Explicit (:pr:`3695`)
-  Introduce ``BaseUpdateProcessor`` for Customized Concurrent Handling of Updates (:pr:`3654` closes :issue:`3509`)

Minor Changes
-------------

-  Fix Inconsistent Type Hints for ``timeout`` Parameter of ``Bot.get_updates`` (:pr:`3709` by `@revolter <https://github.com/revolter>`__)
-  Use Explicit Optionals (:pr:`3692` by `@MiguelX413 <https://github.com/MiguelX413>`__)

Bug Fixes
---------

-  Fix Wrong Warning Text in ``KeyboardButton.__eq__`` (:pr:`3768`)

Documentation Improvements
--------------------------

-  Explicitly set ``allowed_updates`` in Examples (:pr:`3741` by `@Trifase <https://github.com/Trifase>`__ closes :issue:`3726`)
-  Bump ``furo`` and ``sphinx`` (:pr:`3719`)
-  Documentation Improvements (:pr:`3698`, :pr:`3708` by `@revolter <https://github.com/revolter>`__, :pr:`3767`)
-  Add Quotes for Installation Instructions With Optional Dependencies (:pr:`3780`)
-  Exclude Type Hints from Stability Policy (:pr:`3712`)
-  Set ``httpx`` Logging Level to Warning in Examples (:pr:`3746` closes :issue:`3743`)

Internal Changes
----------------

-  Drop a Legacy ``pre-commit.ci`` Configuration (:pr:`3697`)
-  Add Python 3.12 Beta to the Test Matrix (:pr:`3751`)
-  Use Temporary Files for Testing File Downloads (:pr:`3777`)
-  Auto-Update Changed Version in Other Files After Dependabot PRs (:pr:`3716`)
-  Add More ``ruff`` Rules (:pr:`3763`)
-  Rename ``_handler.py`` to ``_basehandler.py`` (:pr:`3761`)
-  Automatically Label ``pre-commit-ci`` PRs (:pr:`3713`)
-  Rework ``pytest`` Integration into GitHub Actions (:pr:`3776`)
-  Fix Two Bugs in GitHub Actions Workflows (:pr:`3739`)

Dependency Updates
------------------

-  Update ``cachetools`` requirement from ~=5.3.0 to ~=5.3.1 (:pr:`3738`)
-  Update ``aiolimiter`` requirement from ~=1.0.0 to ~=1.1.0 (:pr:`3707`)
-  ``pre-commit`` autoupdate (:pr:`3791`)
-  Bump ``sphinxcontrib-mermaid`` from 0.8.1 to 0.9.2 (:pr:`3737`)
-  Bump ``pytest-xdist`` from 3.2.1 to 3.3.0 (:pr:`3705`)
-  Bump ``srvaroa/labeler`` from 1.5.0 to 1.6.0 (:pr:`3786`)
-  Bump ``dependabot/fetch-metadata`` from 1.5.1 to 1.6.0 (:pr:`3787`)
-  Bump ``dessant/lock-threads`` from 4.0.0 to 4.0.1 (:pr:`3785`)
-  Bump ``pytest`` from 7.3.2 to 7.4.0 (:pr:`3774`)
-  Update ``httpx`` requirement from ~=0.24.0 to ~=0.24.1 (:pr:`3715`)
-  Bump ``pytest-xdist`` from 3.3.0 to 3.3.1 (:pr:`3714`)
-  Bump ``pytest`` from 7.3.1 to 7.3.2 (:pr:`3758`)
-  ``pre-commit`` autoupdate (:pr:`3747`)


Version 20.3
============
*Released 2023-05-07*

This is the technical changelog for version 20.3. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full support for API 6.7 (:pr:`3673`)
- Add a Stability Policy (:pr:`3622`)

New Features
------------

- Add ``Application.mark_data_for_update_persistence`` (:pr:`3607`)
- Make ``Message.link`` Point to Thread View Where Possible (:pr:`3640`)
- Localize Received ``datetime`` Objects According to ``Defaults.tzinfo`` (:pr:`3632`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Empower ``ruff`` (:pr:`3594`)
- Drop Usage of ``sys.maxunicode`` (:pr:`3630`)
- Add String Representation for ``RequestParameter`` (:pr:`3634`)
- Stabilize CI by Rerunning Failed Tests (:pr:`3631`)
- Give Loggers Better Names (:pr:`3623`)
- Add Logging for Invalid JSON Data in ``BasePersistence.parse_json_payload`` (:pr:`3668`)
- Improve Warning Categories & Stacklevels (:pr:`3674`)
- Stabilize ``test_delete_sticker_set`` (:pr:`3685`)
- Shield Update Fetcher Task in ``Application.start`` (:pr:`3657`)
- Recover 100% Type Completeness (:pr:`3676`)
- Documentation Improvements (:pr:`3628`, :pr:`3636`, :pr:`3694`)

Dependencies
------------

- Bump ``actions/stale`` from 7 to 8 (:pr:`3644`)
- Bump ``furo`` from 2023.3.23 to 2023.3.27 (:pr:`3643`)
- ``pre-commit`` autoupdate (:pr:`3646`, :pr:`3688`)
- Remove Deprecated ``codecov`` Package from CI (:pr:`3664`)
- Bump ``sphinx-copybutton`` from 0.5.1 to 0.5.2 (:pr:`3662`)
- Update ``httpx`` requirement from ~=0.23.3 to ~=0.24.0 (:pr:`3660`)
- Bump ``pytest`` from 7.2.2 to 7.3.1 (:pr:`3661`)

Version 20.2
============
*Released 2023-03-25*

This is the technical changelog for version 20.2. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------
- Full Support for API 6.6 (:pr:`3584`)
- Revert to HTTP/1.1 as Default and make HTTP/2 an Optional Dependency (:pr:`3576`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------
- Documentation Improvements (:pr:`3565`, :pr:`3600`)
- Handle Symbolic Links in ``was_called_by`` (:pr:`3552`)
- Tidy Up Tests Directory (:pr:`3553`)
- Enhance ``Application.create_task`` (:pr:`3543`)
- Make Type Completeness Workflow Usable for ``PRs`` from Forks (:pr:`3551`)
- Refactor and Overhaul the Test Suite (:pr:`3426`)

Dependencies
------------
- Bump ``pytest-asyncio`` from 0.20.3 to 0.21.0 (:pr:`3624`)
- Bump ``furo`` from 2022.12.7 to 2023.3.23 (:pr:`3625`)
- Bump ``pytest-xdist`` from 3.2.0 to 3.2.1 (:pr:`3606`)
- ``pre-commit`` autoupdate (:pr:`3577`)
- Update ``apscheduler`` requirement from ~=3.10.0 to ~=3.10.1 (:pr:`3572`)
- Bump ``pytest`` from 7.2.1 to 7.2.2 (:pr:`3573`)
- Bump ``pytest-xdist`` from 3.1.0 to 3.2.0 (:pr:`3550`)
- Bump ``sphinxcontrib-mermaid`` from 0.7.1 to 0.8 (:pr:`3549`)

Version 20.1
============
*Released 2023-02-09*

This is the technical changelog for version 20.1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support for Bot API 6.5 (:pr:`3530`)

New Features
------------

- Add ``Application(Builder).post_stop`` (:pr:`3466`)
- Add ``Chat.effective_name`` Convenience Property (:pr:`3485`)
- Allow to Adjust HTTP Version and Use HTTP/2 by Default (:pr:`3506`)

Documentation Improvements
--------------------------

- Enhance ``chatmemberbot`` Example (:pr:`3500`)
- Automatically Generate Cross-Reference Links (:pr:`3501`, :pr:`3529`, :pr:`3523`)
- Add Some Graphic Elements to Docs (:pr:`3535`)
- Various Smaller Improvements (:pr:`3464`, :pr:`3483`, :pr:`3484`, :pr:`3497`, :pr:`3512`, :pr:`3515`,  :pr:`3498`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Update Copyright to 2023 (:pr:`3459`)
- Stabilize Tests on Closing and Hiding the General Forum Topic (:pr:`3460`)
- Fix Dependency Warning Typo (:pr:`3474`)
- Cache Dependencies on ``GitHub`` Actions (:pr:`3469`)
- Store Documentation Builts as ``GitHub`` Actions Artifacts (:pr:`3468`)
- Add ``ruff`` to ``pre-commit`` Hooks (:pr:`3488`)
- Improve Warning for ``days`` Parameter of  ``JobQueue.run_daily`` (:pr:`3503`)
- Improve Error Message for ``NetworkError`` (:pr:`3505`)
- Lock Inactive Threads Only Once Each Day (:pr:`3510`)
- Bump ``pytest`` from 7.2.0 to 7.2.1 (:pr:`3513`)
- Check for 3D Arrays in ``check_keyboard_type`` (:pr:`3514`)
- Explicit Type Annotations (:pr:`3508`)
- Increase Verbosity of Type Completeness CI Job (:pr:`3531`)
- Fix CI on Python 3.11 + Windows (:pr:`3547`)

Dependencies
------------

- Bump ``actions/stale`` from 6 to 7 (:pr:`3461`)
- Bump ``dessant/lock-threads`` from 3.0.0 to 4.0.0 (:pr:`3462`)
- ``pre-commit`` autoupdate (:pr:`3470`)
- Update ``httpx`` requirement from ~=0.23.1 to ~=0.23.3 (:pr:`3489`)
- Update ``cachetools`` requirement from ~=5.2.0 to ~=5.2.1 (:pr:`3502`)
- Improve Config for ``ruff`` and Bump to ``v0.0.222`` (:pr:`3507`)
- Update ``cachetools`` requirement from ~=5.2.1 to ~=5.3.0 (:pr:`3520`)
- Bump ``isort`` to 5.12.0 (:pr:`3525`)
- Update ``apscheduler`` requirement from ~=3.9.1 to ~=3.10.0 (:pr:`3532`)
- ``pre-commit`` autoupdate (:pr:`3537`)
- Update ``cryptography`` requirement to >=39.0.1 to address Vulnerability (:pr:`3539`)

Version 20.0
============
*Released 2023-01-01*

This is the technical changelog for version 20.0. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support For Bot API 6.4 (:pr:`3449`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Documentation Improvements (:pr:`3428`, :pr:`3423`, :pr:`3429`, :pr:`3441`, :pr:`3404`, :pr:`3443`)
- Allow ``Sequence`` Input for Bot Methods (:pr:`3412`)
- Update Link-Check CI and Replace a Dead Link (:pr:`3456`)
- Freeze Classes Without Arguments (:pr:`3453`)
- Add New Constants (:pr:`3444`)
- Override ``Bot.__deepcopy__`` to Raise ``TypeError`` (:pr:`3446`)
- Add Log Decorator to ``Bot.get_webhook_info`` (:pr:`3442`)
- Add Documentation On Verifying Releases (:pr:`3436`)
- Drop Undocumented ``Job.__lt__`` (:pr:`3432`)

Dependencies
------------

- Downgrade ``sphinx`` to 5.3.0 to Fix Search (:pr:`3457`)
- Bump ``sphinx`` from 5.3.0 to 6.0.0 (:pr:`3450`)

Version 20.0b0
==============
*Released 2022-12-15*

This is the technical changelog for version 20.0b0. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Make ``TelegramObject`` Immutable (:pr:`3249`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Reduce Code Duplication in Testing ``Defaults`` (:pr:`3419`)
- Add Notes and Warnings About Optional Dependencies (:pr:`3393`)
- Simplify Internals of ``Bot`` Methods (:pr:`3396`)
- Reduce Code Duplication in Several ``Bot`` Methods (:pr:`3385`)
- Documentation Improvements (:pr:`3386`, :pr:`3395`, :pr:`3398`, :pr:`3403`)

Dependencies
------------

- Bump ``pytest-xdist`` from 3.0.2 to 3.1.0 (:pr:`3415`)
- Bump ``pytest-asyncio`` from 0.20.2 to 0.20.3 (:pr:`3417`)
- ``pre-commit`` autoupdate (:pr:`3409`)

Version 20.0a6
==============
*Released 2022-11-24*

This is the technical changelog for version 20.0a6. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Bug Fixes
---------

- Only Persist Arbitrary ``callback_data`` if ``ExtBot.callback_data_cache`` is Present (:pr:`3384`)
- Improve Backwards Compatibility of ``TelegramObjects`` Pickle Behavior (:pr:`3382`)
- Fix Naming and Keyword Arguments of ``File.download_*`` Methods (:pr:`3380`)
- Fix Return Value Annotation of ``Chat.create_forum_topic`` (:pr:`3381`)

Version 20.0a5
==============
*Released 2022-11-22*

This is the technical changelog for version 20.0a5. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- API 6.3 (:pr:`3346`, :pr:`3343`, :pr:`3342`, :pr:`3360`)
- Explicit ``local_mode`` Setting (:pr:`3154`)
- Make Almost All 3rd Party Dependencies Optional (:pr:`3267`)
- Split ``File.download`` Into ``File.download_to_drive`` And ``File.download_to_memory`` (:pr:`3223`)

New Features
------------

- Add Properties for API Settings of ``Bot`` (:pr:`3247`)
- Add ``chat_id`` and ``username`` Parameters to ``ChatJoinRequestHandler`` (:pr:`3261`)
- Introduce ``TelegramObject.api_kwargs`` (:pr:`3233`)
- Add Two Constants Related to Local Bot API Servers (:pr:`3296`)
- Add ``recursive`` Parameter to ``TelegramObject.to_dict()`` (:pr:`3276`)
- Overhaul String Representation of ``TelegramObject`` (:pr:`3234`)
- Add Methods ``Chat.mention_{html, markdown, markdown_v2}`` (:pr:`3308`)
- Add ``constants.MessageLimit.DEEP_LINK_LENGTH`` (:pr:`3315`)
- Add Shortcut Parameters ``caption``, ``parse_mode`` and ``caption_entities`` to ``Bot.send_media_group`` (:pr:`3295`)
- Add Several New Enums To Constants (:pr:`3351`)

Bug Fixes
---------

- Fix ``CallbackQueryHandler`` Not Handling Non-String Data Correctly With Regex Patterns (:pr:`3252`)
- Fix Defaults Handling in ``Bot.answer_web_app_query`` (:pr:`3362`)

Documentation Improvements
--------------------------

- Update PR Template (:pr:`3361`)
- Document Dunder Methods of ``TelegramObject`` (:pr:`3319`)
- Add Several References to Wiki pages (:pr:`3306`)
- Overhaul Search bar (:pr:`3218`)
- Unify Documentation of Arguments and Attributes of Telegram Classes (:pr:`3217`, :pr:`3292`, :pr:`3303`, :pr:`3312`, :pr:`3314`)
- Several Smaller Improvements (:pr:`3214`, :pr:`3271`, :pr:`3289`, :pr:`3326`, :pr:`3370`, :pr:`3376`, :pr:`3366`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Improve Warning About Unknown ``ConversationHandler`` States (:pr:`3242`)
- Switch from Stale Bot to ``GitHub`` Actions (:pr:`3243`)
- Bump Python 3.11 to RC2 in Test Matrix (:pr:`3246`)
- Make ``Job.job`` a Property and Make ``Jobs`` Hashable (:pr:`3250`)
- Skip ``JobQueue`` Tests on Windows Again (:pr:`3280`)
- Read-Only ``CallbackDataCache`` (:pr:`3266`)
- Type Hinting Fix for ``Message.effective_attachment`` (:pr:`3294`)
- Run Unit Tests in Parallel (:pr:`3283`)
- Update Test Matrix to Use Stable Python 3.11 (:pr:`3313`)
- Don't Edit Objects In-Place When Inserting ``ext.Defaults`` (:pr:`3311`)
- Add a Test for ``MessageAttachmentType`` (:pr:`3335`)
- Add Three New Test Bots (:pr:`3347`)
- Improve Unit Tests Regarding ``ChatMemberUpdated.difference`` (:pr:`3352`)
- Flaky Unit Tests: Use ``pytest`` Marker (:pr:`3354`)
- Fix ``DeepSource`` Issues (:pr:`3357`)
- Handle Lists and Tuples and Datetimes Directly in ``TelegramObject.to_dict`` (:pr:`3353`)
- Update Meta Config (:pr:`3365`)
- Merge ``ChatDescriptionLimit`` Enum Into ``ChatLimit`` (:pr:`3377`)

Dependencies
------------

- Bump ``pytest`` from 7.1.2 to 7.1.3 (:pr:`3228`)
- ``pre-commit`` Updates (:pr:`3221`)
- Bump ``sphinx`` from 5.1.1 to 5.2.3 (:pr:`3269`)
- Bump ``furo`` from 2022.6.21 to 2022.9.29 (:pr:`3268`)
- Bump ``actions/stale`` from 5 to 6 (:pr:`3277`)
- ``pre-commit`` autoupdate (:pr:`3282`)
- Bump ``sphinx`` from 5.2.3 to 5.3.0 (:pr:`3300`)
- Bump ``pytest-asyncio`` from 0.19.0 to 0.20.1 (:pr:`3299`)
- Bump ``pytest`` from 7.1.3 to 7.2.0 (:pr:`3318`)
- Bump ``pytest-xdist`` from 2.5.0 to 3.0.2 (:pr:`3317`)
- ``pre-commit`` autoupdate (:pr:`3325`)
- Bump ``pytest-asyncio`` from 0.20.1 to 0.20.2 (:pr:`3359`)
- Update ``httpx`` requirement from ~=0.23.0 to ~=0.23.1 (:pr:`3373`)

Version 20.0a4
==============
*Released 2022-08-27*

This is the technical changelog for version 20.0a4. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Hot Fixes
---------

* Fix a Bug in ``setup.py`` Regarding Optional Dependencies (:pr:`3209`)

Version 20.0a3
==============
*Released 2022-08-27*

This is the technical changelog for version 20.0a3. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support for API 6.2 (:pr:`3195`)

New Features
------------

- New Rate Limiting Mechanism (:pr:`3148`)
- Make ``chat/user_data`` Available in Error Handler for Errors in Jobs (:pr:`3152`)
- Add ``Application.post_shutdown`` (:pr:`3126`)

Bug Fixes
---------

- Fix ``helpers.mention_markdown`` for Markdown V1 and Improve Related Unit Tests (:pr:`3155`)
- Add ``api_kwargs`` Parameter to ``Bot.log_out`` and Improve Related Unit Tests (:pr:`3147`)
- Make ``Bot.delete_my_commands`` a Coroutine Function (:pr:`3136`)
- Fix ``ConversationHandler.check_update`` not respecting ``per_user`` (:pr:`3128`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Add Python 3.11 to Test Suite & Adapt Enum Behaviour (:pr:`3168`)
- Drop Manual Token Validation (:pr:`3167`)
- Simplify Unit Tests for ``Bot.send_chat_action`` (:pr:`3151`)
- Drop ``pre-commit`` Dependencies from ``requirements-dev.txt`` (:pr:`3120`)
- Change Default Values for ``concurrent_updates`` and ``connection_pool_size`` (:pr:`3127`)
- Documentation Improvements (:pr:`3139`, :pr:`3153`, :pr:`3135`)
- Type Hinting Fixes (:pr:`3202`)

Dependencies
------------

- Bump ``sphinx`` from 5.0.2 to 5.1.1 (:pr:`3177`)
- Update ``pre-commit`` Dependencies (:pr:`3085`)
- Bump ``pytest-asyncio`` from 0.18.3 to 0.19.0 (:pr:`3158`)
- Update ``tornado`` requirement from ~=6.1 to ~=6.2 (:pr:`3149`)
- Bump ``black`` from 22.3.0 to 22.6.0 (:pr:`3132`)
- Bump ``actions/setup-python`` from 3 to 4 (:pr:`3131`)

Version 20.0a2
==============
*Released 2022-06-27*

This is the technical changelog for version 20.0a2. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes
-------------

- Full Support for API 6.1 (:pr:`3112`)

New Features
------------

- Add Additional Shortcut Methods to ``Chat`` (:pr:`3115`)
- Mermaid-based Example State Diagrams (:pr:`3090`)

Minor Changes, Documentation Improvements and CI
------------------------------------------------

- Documentation Improvements (:pr:`3103`, :pr:`3121`, :pr:`3098`)
- Stabilize CI (:pr:`3119`)
- Bump ``pyupgrade`` from 2.32.1 to 2.34.0 (:pr:`3096`)
- Bump ``furo`` from 2022.6.4 to 2022.6.4.1 (:pr:`3095`)
- Bump ``mypy`` from 0.960 to 0.961 (:pr:`3093`)

Version 20.0a1
==============
*Released 2022-06-09*

This is the technical changelog for version 20.0a1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes:
--------------

- Drop Support for ``ujson`` and instead ``BaseRequest.parse_json_payload`` (:pr:`3037`, :pr:`3072`)
- Drop ``InputFile.is_image`` (:pr:`3053`)
- Drop Explicit Type conversions in ``__init__`` s (:pr:`3056`)
- Handle List-Valued Attributes More Consistently (:pr:`3057`)
- Split ``{Command, Prefix}Handler`` And Make Attributes Immutable (:pr:`3045`)
- Align Behavior Of ``JobQueue.run_daily`` With ``cron`` (:pr:`3046`)
- Make PTB Specific  Keyword-Only Arguments for PTB Specific in Bot methods (:pr:`3035`)
- Adjust Equality Comparisons to Fit Bot API 6.0 (:pr:`3033`)
- Add Tuple Based Version Info (:pr:`3030`)
- Improve Type Annotations for ``CallbackContext`` and Move Default Type Alias to ``ContextTypes.DEFAULT_TYPE`` (:pr:`3017`, :pr:`3023`)
- Rename ``Job.context`` to ``Job.data`` (:pr:`3028`)
- Rename ``Handler`` to ``BaseHandler`` (:pr:`3019`)

New Features:
-------------

- Add ``Application.post_init`` (:pr:`3078`)
- Add Arguments ``chat/user_id`` to ``CallbackContext`` And Example On Custom Webhook Setups (:pr:`3059`)
- Add Convenience Property ``Message.id`` (:pr:`3077`)
- Add Example for ``WebApp`` (:pr:`3052`)
- Rename ``telegram.bot_api_version`` to ``telegram.__bot_api_version__`` (:pr:`3030`)

Bug Fixes:
----------

- Fix Non-Blocking Entry Point in ``ConversationHandler`` (:pr:`3068`)
- Escape Backslashes in ``escape_markdown``  (:pr:`3055`)

Dependencies:
-------------

- Update ``httpx`` requirement from ~=0.22.0 to ~=0.23.0 (:pr:`3069`)
- Update ``cachetools`` requirement from ~=5.0.0 to ~=5.2.0 (:pr:`3058`, :pr:`3080`)

Minor Changes, Documentation Improvements and CI:
-------------------------------------------------

- Move Examples To Documentation (:pr:`3089`)
- Documentation Improvements and Update Dependencies (:pr:`3010`, :pr:`3007`, :pr:`3012`, :pr:`3067`, :pr:`3081`, :pr:`3082`)
- Improve Some Unit Tests (:pr:`3026`)
- Update Code Quality dependencies (:pr:`3070`, :pr:`3032`,:pr:`2998`, :pr:`2999`)
- Don't Set Signal Handlers On Windows By Default (:pr:`3065`)
- Split ``{Command, Prefix}Handler`` And Make Attributes Immutable (:pr:`3045`)
- Apply ``isort`` and Update ``pre-commit.ci`` Configuration (:pr:`3049`)
- Adjust ``pre-commit`` Settings for ``isort`` (:pr:`3043`)
- Add Version Check to Examples (:pr:`3036`)
- Use ``Collection`` Instead of ``List`` and ``Tuple`` (:pr:`3025`)
- Remove Client-Side Parameter Validation (:pr:`3024`)
- Don't Pass Default Values of Optional Parameters to Telegram (:pr:`2978`)
- Stabilize ``Application.run_*`` on Python 3.7 (:pr:`3009`)
- Ignore Code Style Commits in ``git blame`` (:pr:`3003`)
- Adjust Tests to Changed API Behavior (:pr:`3002`)

Version 20.0a0
==============
*Released 2022-05-06*

This is the technical changelog for version 20.0a0. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

Major Changes:
--------------

-  Refactor Initialization of Persistence Classes
   (:pr:`2604`)
-  Drop Non-``CallbackContext`` API
   (:pr:`2617`)
-  Remove ``__dict__`` from ``__slots__`` and drop Python 3.6
   (:pr:`2619`,
   :pr:`2636`)
-  Move and Rename ``TelegramDecryptionError`` to
   ``telegram.error.PassportDecryptionError``
   (:pr:`2621`)
-  Make ``BasePersistence`` Methods Abstract
   (:pr:`2624`)
-  Remove ``day_is_strict`` argument of ``JobQueue.run_monthly``
   (:pr:`2634`
   by `iota-008 <https://github.com/iota-008>`__)
-  Move ``Defaults`` to ``telegram.ext``
   (:pr:`2648`)
-  Remove Deprecated Functionality
   (:pr:`2644`,
   :pr:`2740`,
   :pr:`2745`)
-  Overhaul of Filters
   (:pr:`2759`,
   :pr:`2922`)
-  Switch to ``asyncio`` and Refactor PTBs Architecture
   (:pr:`2731`)
-  Improve ``Job.__getattr__``
   (:pr:`2832`)
-  Remove ``telegram.ReplyMarkup``
   (:pr:`2870`)
-  Persistence of ``Bots``: Refactor Automatic Replacement and
   Integration with ``TelegramObject``
   (:pr:`2893`)

New Features:
-------------

-  Introduce Builder Pattern
   (:pr:`2646`)
-  Add ``Filters.update.edited``
   (:pr:`2705`
   by `PhilippFr <https://github.com/PhilippFr>`__)
-  Introduce ``Enums`` for ``telegram.constants``
   (:pr:`2708`)
-  Accept File Paths for ``private_key``
   (:pr:`2724`)
-  Associate ``Jobs`` with ``chat/user_id``
   (:pr:`2731`)
-  Convenience Functionality for ``ChatInviteLinks``
   (:pr:`2782`)
-  Add ``Dispatcher.add_handlers``
   (:pr:`2823`)
-  Improve Error Messages in ``CommandHandler.__init__``
   (:pr:`2837`)
-  ``Defaults.protect_content``
   (:pr:`2840`)
-  Add ``Dispatcher.migrate_chat_data``
   (:pr:`2848`
   by `DonalDuck004 <https://github.com/DonalDuck004>`__)
-  Add Method ``drop_chat/user_data`` to ``Dispatcher`` and Persistence
   (:pr:`2852`)
-  Add methods ``ChatPermissions.{all, no}_permissions`` (:pr:`2948`)
-  Full Support for API 6.0
   (:pr:`2956`)
-  Add Python 3.10 to Test Suite
   (:pr:`2968`)

Bug Fixes & Minor Changes:
--------------------------

-  Improve Type Hinting for ``CallbackContext``
   (:pr:`2587`
   by `revolter <https://github.com/revolter>`__)
-  Fix Signatures and Improve ``test_official``
   (:pr:`2643`)
-  Refine ``Dispatcher.dispatch_error``
   (:pr:`2660`)
-  Make ``InlineQuery.answer`` Raise ``ValueError``
   (:pr:`2675`)
-  Improve Signature Inspection for Bot Methods
   (:pr:`2686`)
-  Introduce ``TelegramObject.set/get_bot``
   (:pr:`2712`
   by `zpavloudis <https://github.com/zpavloudis>`__)
-  Improve Subscription of ``TelegramObject``
   (:pr:`2719`
   by `SimonDamberg <https://github.com/SimonDamberg>`__)
-  Use Enums for Dynamic Types & Rename Two Attributes in ``ChatMember``
   (:pr:`2817`)
-  Return Plain Dicts from ``BasePersistence.get_*_data``
   (:pr:`2873`)
-  Fix a Bug in ``ChatMemberUpdated.difference``
   (:pr:`2947`)
-  Update Dependency Policy
   (:pr:`2958`)

Internal Restructurings & Improvements:
---------------------------------------

-  Add User Friendly Type Check For Init Of
   ``{Inline, Reply}KeyboardMarkup``
   (:pr:`2657`)
-  Warnings Overhaul
   (:pr:`2662`)
-  Clear Up Import Policy
   (:pr:`2671`)
-  Mark Internal Modules As Private
   (:pr:`2687`
   by `kencx <https://github.com/kencx>`__)
-  Handle Filepaths via the ``pathlib`` Module
   (:pr:`2688`
   by `eldbud <https://github.com/eldbud>`__)
-  Refactor MRO of ``InputMedia*`` and Some File-Like Classes
   (:pr:`2717`
   by `eldbud <https://github.com/eldbud>`__)
-  Update Exceptions for Immutable Attributes
   (:pr:`2749`)
-  Refactor Warnings in ``ConversationHandler``
   (:pr:`2755`,
   :pr:`2784`)
-  Use ``__all__`` Consistently
   (:pr:`2805`)

CI, Code Quality & Test Suite Improvements:
-------------------------------------------

-  Add Custom ``pytest`` Marker to Ease Development
   (:pr:`2628`)
-  Pass Failing Jobs to Error Handlers
   (:pr:`2692`)
-  Update Notification Workflows
   (:pr:`2695`)
-  Use Error Messages for ``pylint`` Instead of Codes
   (:pr:`2700`
   by `Piraty <https://github.com/Piraty>`__)
-  Make Tests Agnostic of the CWD
   (:pr:`2727`
   by `eldbud <https://github.com/eldbud>`__)
-  Update Code Quality Dependencies
   (:pr:`2748`)
-  Improve Code Quality
   (:pr:`2783`)
-  Update ``pre-commit`` Settings & Improve a Test
   (:pr:`2796`)
-  Improve Code Quality & Test Suite
   (:pr:`2843`)
-  Fix failing animation tests
   (:pr:`2865`)
-  Update and Expand Tests & pre-commit Settings and Improve Code
   Quality
   (:pr:`2925`)
-  Extend Code Formatting With Black
   (:pr:`2972`)
-  Update Workflow Permissions
   (:pr:`2984`)
-  Adapt Tests to Changed ``Bot.get_file`` Behavior
   (:pr:`2995`)

Documentation Improvements:
---------------------------

-  Doc Fixes
   (:pr:`2597`)
-  Add Code Comment Guidelines to Contribution Guide
   (:pr:`2612`)
-  Add Cross-References to External Libraries & Other Documentation
   Improvements
   (:pr:`2693`,
   :pr:`2691`
   by `joesinghh <https://github.com/joesinghh>`__,
   :pr:`2739`
   by `eldbud <https://github.com/eldbud>`__)
-  Use Furo Theme, Make Parameters Referenceable, Add Documentation
   Building to CI, Improve Links to Source Code & Other Improvements
   (:pr:`2856`,
   :pr:`2798`,
   :pr:`2854`,
   :pr:`2841`)
-  Documentation Fixes & Improvements
   (:pr:`2822`)
-  Replace ``git.io`` Links
   (:pr:`2872`
   by `murugu-21 <https://github.com/murugu-21>`__)
-  Overhaul Readmes, Update RTD Startpage & Other Improvements
   (:pr:`2969`)

Version 13.11
=============
*Released 2022-02-02*

This is the technical changelog for version 13.11. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full Support for Bot API 5.7 (:pr:`2881`)

Version 13.10
=============
*Released 2022-01-03*

This is the technical changelog for version 13.10. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full Support for API 5.6 (:pr:`2835`)

**Minor Changes & Doc fixes:**

- Update Copyright to 2022 (:pr:`2836`)
- Update Documentation of ``BotCommand`` (:pr:`2820`)

Version 13.9
============
*Released 2021-12-11*

This is the technical changelog for version 13.9. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full Support for Api 5.5 (:pr:`2809`)

**Minor Changes**

- Adjust Automated Locking of Inactive Issues (:pr:`2775`)

Version 13.8.1
==============
*Released 2021-11-08*

This is the technical changelog for version 13.8.1. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Doc fixes:**

- Add ``ChatJoinRequest(Handler)`` to Docs (:pr:`2771`)

Version 13.8
============
*Released 2021-11-08*

This is the technical changelog for version 13.8. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full support for API 5.4 (:pr:`2767`)

**Minor changes, CI improvements, Doc fixes and Type hinting:**

- Create Issue Template Forms (:pr:`2689`)
- Fix ``camelCase`` Functions in ``ExtBot`` (:pr:`2659`)
- Fix Empty Captions not Being Passed by ``Bot.copy_message`` (:pr:`2651`)
- Fix Setting Thumbs When Uploading A Single File (:pr:`2583`)
- Fix Bug in ``BasePersistence.insert``/``replace_bot`` for Objects with ``__dict__`` not in ``__slots__`` (:pr:`2603`)

Version 13.7
============
*Released 2021-07-01*

This is the technical changelog for version 13.7. More elaborate release notes can be found in the news channel `@pythontelegrambotchannel <https://t.me/pythontelegrambotchannel>`_.

**Major Changes:**

- Full support for Bot API 5.3 (:pr:`2572`)

**Bug Fixes:**

- Fix Bug in ``BasePersistence.insert/replace_bot`` for Objects with ``__dict__`` in their slots (:pr:`2561`)
- Remove Incorrect Warning About ``Defaults`` and ``ExtBot`` (:pr:`2553`)

**Minor changes, CI improvements, Doc fixes and Type hinting:**

- Type Hinting Fixes (:pr:`2552`)
- Doc Fixes (:pr:`2551`)
- Improve Deprecation Warning for ``__slots__`` (:pr:`2574`)
- Stabilize CI (:pr:`2575`)
- Fix Coverage Configuration (:pr:`2571`)
- Better Exception-Handling for ``BasePersistence.replace/insert_bot`` (:pr:`2564`)
- Remove Deprecated ``pass_args`` from Deeplinking Example (:pr:`2550`)

Version 13.6
============
*Released 2021-06-06*

New Features:

- Arbitrary ``callback_data`` (:pr:`1844`)
- Add ``ContextTypes`` & ``BasePersistence.refresh_user/chat/bot_data`` (:pr:`2262`)
- Add ``Filters.attachment`` (:pr:`2528`)
- Add ``pattern`` Argument to ``ChosenInlineResultHandler`` (:pr:`2517`)

Major Changes:

- Add ``slots`` (:pr:`2345`)

Minor changes, CI improvements, Doc fixes and Type hinting:

- Doc Fixes (:pr:`2495`, :pr:`2510`)
- Add ``max_connections`` Parameter to ``Updater.start_webhook`` (:pr:`2547`)
- Fix for ``Promise.done_callback`` (:pr:`2544`)
- Improve Code Quality (:pr:`2536`, :pr:`2454`)
- Increase Test Coverage of ``CallbackQueryHandler`` (:pr:`2520`)
- Stabilize CI (:pr:`2522`, :pr:`2537`, :pr:`2541`)
- Fix ``send_phone_number_to_provider`` argument for ``Bot.send_invoice`` (:pr:`2527`)
- Handle Classes as Input for ``BasePersistence.replace/insert_bot`` (:pr:`2523`)
- Bump Tornado Version and Remove Workaround from :pr:`2067` (:pr:`2494`)

Version 13.5
============
*Released 2021-04-30*

**Major Changes:**

- Full support of Bot API 5.2 (:pr:`2489`).

  .. note::
     The ``start_parameter`` argument of ``Bot.send_invoice`` and the corresponding shortcuts is now optional, so the order of
     parameters had to be changed. Make sure to update your method calls accordingly.

- Update ``ChatActions``, Deprecating ``ChatAction.RECORD_AUDIO`` and ``ChatAction.UPLOAD_AUDIO`` (:pr:`2460`)

**New Features:**

- Convenience Utilities & Example for Handling ``ChatMemberUpdated`` (:pr:`2490`)
- ``Filters.forwarded_from`` (:pr:`2446`)

**Minor changes, CI improvements, Doc fixes and Type hinting:**

- Improve Timeouts in ``ConversationHandler`` (:pr:`2417`)
- Stabilize CI (:pr:`2480`)
- Doc Fixes (:pr:`2437`)
- Improve Type Hints of Data Filters (:pr:`2456`)
- Add Two ``UserWarnings`` (:pr:`2464`)
- Improve Code Quality (:pr:`2450`)
- Update Fallback Test-Bots (:pr:`2451`)
- Improve Examples (:pr:`2441`, :pr:`2448`)

Version 13.4.1
==============
*Released 2021-03-14*

**Hot fix release:**

- Fixed a bug in ``setup.py`` (:pr:`2431`)

Version 13.4
============
*Released 2021-03-14*

**Major Changes:**

- Full support of Bot API 5.1 (:pr:`2424`)

**Minor changes, CI improvements, doc fixes and type hinting:**

- Improve ``Updater.set_webhook`` (:pr:`2419`)
- Doc Fixes (:pr:`2404`)
- Type Hinting Fixes (:pr:`2425`)
- Update ``pre-commit`` Settings (:pr:`2415`)
- Fix Logging for Vendored ``urllib3`` (:pr:`2427`)
- Stabilize Tests (:pr:`2409`)

Version 13.3
============
*Released 2021-02-19*

**Major Changes:**

- Make ``cryptography`` Dependency Optional & Refactor Some Tests (:pr:`2386`, :pr:`2370`)
- Deprecate ``MessageQueue`` (:pr:`2393`)

**Bug Fixes:**

- Refactor ``Defaults`` Integration (:pr:`2363`)
- Add Missing ``telegram.SecureValue`` to init and Docs (:pr:`2398`)

**Minor changes:**

- Doc Fixes (:pr:`2359`)

Version 13.2
============
*Released 2021-02-02*

**Major Changes:**

- Introduce ``python-telegram-bot-raw`` (:pr:`2324`)
- Explicit Signatures for Shortcuts (:pr:`2240`)

**New Features:**

- Add Missing Shortcuts to ``Message`` (:pr:`2330`)
- Rich Comparison for ``Bot`` (:pr:`2320`)
- Add ``run_async`` Parameter to ``ConversationHandler`` (:pr:`2292`)
- Add New Shortcuts to ``Chat`` (:pr:`2291`)
- Add New Constant ``MAX_ANSWER_CALLBACK_QUERY_TEXT_LENGTH`` (:pr:`2282`)
- Allow Passing Custom Filename For All Media (:pr:`2249`)
- Handle Bytes as File Input (:pr:`2233`)

**Bug Fixes:**

- Fix Escaping in Nested Entities in ``Message`` Properties (:pr:`2312`)
- Adjust Calling of ``Dispatcher.update_persistence`` (:pr:`2285`)
- Add ``quote`` kwarg to ``Message.reply_copy`` (:pr:`2232`)
- ``ConversationHandler``: Docs & ``edited_channel_post`` behavior (:pr:`2339`)

**Minor changes, CI improvements, doc fixes and type hinting:**

- Doc Fixes (:pr:`2253`, :pr:`2225`)
- Reduce Usage of ``typing.Any`` (:pr:`2321`)
- Extend Deeplinking Example (:pr:`2335`)
- Add pyupgrade to pre-commit Hooks (:pr:`2301`)
- Add PR Template (:pr:`2299`)
- Drop Nightly Tests & Update Badges (:pr:`2323`)
- Update Copyright (:pr:`2289`, :pr:`2287`)
- Change Order of Class DocStrings (:pr:`2256`)
- Add macOS to Test Matrix (:pr:`2266`)
- Start Using Versioning Directives in Docs (:pr:`2252`)
- Improve Annotations & Docs of Handlers (:pr:`2243`)

Version 13.1
============
*Released 2020-11-29*

**Major Changes:**

- Full support of Bot API 5.0 (:pr:`2181`, :pr:`2186`, :pr:`2190`, :pr:`2189`, :pr:`2183`, :pr:`2184`, :pr:`2188`, :pr:`2185`, :pr:`2192`, :pr:`2196`, :pr:`2193`, :pr:`2223`, :pr:`2199`, :pr:`2187`, :pr:`2147`, :pr:`2205`)

**New Features:**

- Add ``Defaults.run_async`` (:pr:`2210`)
- Improve and Expand ``CallbackQuery`` Shortcuts (:pr:`2172`)
- Add XOR Filters and make ``Filters.name`` a Property (:pr:`2179`)
- Add ``Filters.document.file_extension`` (:pr:`2169`)
- Add ``Filters.caption_regex`` (:pr:`2163`)
- Add ``Filters.chat_type`` (:pr:`2128`)
- Handle Non-Binary File Input (:pr:`2202`)

**Bug Fixes:**

- Improve Handling of Custom Objects in ``BasePersistence.insert``/``replace_bot`` (:pr:`2151`)
- Fix bugs in ``replace/insert_bot`` (:pr:`2218`)

**Minor changes, CI improvements, doc fixes and type hinting:**

- Improve Type hinting (:pr:`2204`, :pr:`2118`, :pr:`2167`, :pr:`2136`)
- Doc Fixes & Extensions (:pr:`2201`, :pr:`2161`)
- Use F-Strings Where Possible (:pr:`2222`)
- Rename kwargs to _kwargs where possible (:pr:`2182`)
- Comply with PEP561 (:pr:`2168`)
- Improve Code Quality (:pr:`2131`)
- Switch Code Formatting to Black (:pr:`2122`, :pr:`2159`, :pr:`2158`)
- Update Wheel Settings (:pr:`2142`)
- Update ``timerbot.py`` to ``v13.0`` (:pr:`2149`)
- Overhaul Constants (:pr:`2137`)
- Add Python 3.9 to Test Matrix (:pr:`2132`)
- Switch Codecov to ``GitHub`` Action (:pr:`2127`)
- Specify Required pytz Version (:pr:`2121`)

Version 13.0
============
*Released 2020-10-07*

**For a detailed guide on how to migrate from v12 to v13, see this** `wiki page <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-13.0>`_.

**Major Changes:**

- Deprecate old-style callbacks, i.e. set ``use_context=True`` by default (:pr:`2050`)
- Refactor Handling of Message VS Update Filters (:pr:`2032`)
- Deprecate ``Message.default_quote`` (:pr:`1965`)
- Refactor persistence of Bot instances (:pr:`1994`)
- Refactor ``JobQueue`` (:pr:`1981`)
- Refactor handling of kwargs in Bot methods (:pr:`1924`)
- Refactor ``Dispatcher.run_async``, deprecating the ``@run_async`` decorator (:pr:`2051`)

**New Features:**

- Type Hinting (:pr:`1920`)
- Automatic Pagination for ``answer_inline_query`` (:pr:`2072`)
- ``Defaults.tzinfo`` (:pr:`2042`)
- Extend rich comparison of objects (:pr:`1724`)
- Add ``Filters.via_bot`` (:pr:`2009`)
- Add missing shortcuts (:pr:`2043`)
- Allow ``DispatcherHandlerStop`` in ``ConversationHandler`` (:pr:`2059`)
- Make Errors picklable (:pr:`2106`)

**Minor changes, CI improvements, doc fixes or bug fixes:**

- Fix Webhook not working on Windows with Python 3.8+ (:pr:`2067`)
- Fix setting thumbs with ``send_media_group`` (:pr:`2093`)
- Make ``MessageHandler`` filter for ``Filters.update`` first (:pr:`2085`)
- Fix ``PicklePersistence.flush()`` with only ``bot_data`` (:pr:`2017`)
- Add test for clean argument of ``Updater.start_polling/webhook`` (:pr:`2002`)
- Doc fixes, refinements and additions (:pr:`2005`, :pr:`2008`, :pr:`2089`, :pr:`2094`, :pr:`2090`)
- CI fixes (:pr:`2018`, :pr:`2061`)
- Refine ``pollbot.py`` example (:pr:`2047`)
- Refine Filters in examples (:pr:`2027`)
- Rename ``echobot`` examples (:pr:`2025`)
- Use Lock-Bot to lock old threads (:pr:`2048`, :pr:`2052`, :pr:`2049`, :pr:`2053`)

Version 12.8
============
*Released 2020-06-22*

**Major Changes:**

- Remove Python 2 support (:pr:`1715`)
- Bot API 4.9 support (:pr:`1980`)
- IDs/Usernames of ``Filters.user`` and ``Filters.chat`` can now be updated (:pr:`1757`)

**Minor changes, CI improvements, doc fixes or bug fixes:**

- Update contribution guide and stale bot (:pr:`1937`)
- Remove ``NullHandlers`` (:pr:`1913`)
- Improve and expand examples (:pr:`1943`, :pr:`1995`, :pr:`1983`, :pr:`1997`)
- Doc fixes (:pr:`1940`, :pr:`1962`)
- Add ``User.send_poll()`` shortcut (:pr:`1968`)
- Ignore private attributes en ``TelegramObject.to_dict()`` (:pr:`1989`)
- Stabilize CI (:pr:`2000`)

Version 12.7
============
*Released 2020-05-02*

**Major Changes:**

- Bot API 4.8 support. **Note:** The ``Dice`` object now has a second positional argument ``emoji``. This is relevant, if you instantiate ``Dice`` objects manually. (:pr:`1917`)
- Added ``tzinfo`` argument to ``helpers.from_timestamp``. It now returns an timezone aware object. This is relevant for ``Message.{date,forward_date,edit_date}``, ``Poll.close_date`` and ``ChatMember.until_date`` (:pr:`1621`)

**New Features:**

- New method ``run_monthly`` for the ``JobQueue`` (:pr:`1705`)
- ``Job.next_t`` now gives the datetime of the jobs next execution (:pr:`1685`)

**Minor changes, CI improvements, doc fixes or bug fixes:**

- Stabalize CI (:pr:`1919`, :pr:`1931`)
- Use ABCs ``@abstractmethod`` instead of raising ``NotImplementedError`` for ``Handler``, ``BasePersistence`` and ``BaseFilter`` (:pr:`1905`)
- Doc fixes (:pr:`1914`, :pr:`1902`, :pr:`1910`)

Version 12.6.1
==============
*Released 2020-04-11*

**Bug fixes:**

- Fix serialization of ``reply_markup`` in media messages (:pr:`1889`)

Version 12.6
============
*Released 2020-04-10*

**Major Changes:**

- Bot API 4.7 support. **Note:** In ``Bot.create_new_sticker_set`` and ``Bot.add_sticker_to_set``, the order of the parameters had be changed, as the ``png_sticker`` parameter is now optional. (:pr:`1858`)

**Minor changes, CI improvements or bug fixes:**

- Add tests for ``swtich_inline_query(_current_chat)`` with empty string (:pr:`1635`)
- Doc fixes (:pr:`1854`, :pr:`1874`, :pr:`1884`)
- Update issue templates (:pr:`1880`)
- Favor concrete types over "Iterable" (:pr:`1882`)
- Pass last valid ``CallbackContext`` to ``TIMEOUT`` handlers of ``ConversationHandler`` (:pr:`1826`)
- Tweak handling of persistence and update persistence after job calls (:pr:`1827`)
- Use checkout@v2 for GitHub actions (:pr:`1887`)

Version 12.5.1
==============
*Released 2020-03-30*

**Minor changes, doc fixes or bug fixes:**

- Add missing docs for `PollHandler` and `PollAnswerHandler` (:pr:`1853`)
- Fix wording in `Filters` docs (:pr:`1855`)
- Reorder tests to make them more stable (:pr:`1835`)
- Make `ConversationHandler` attributes immutable (:pr:`1756`)
- Make `PrefixHandler` attributes `command` and `prefix` editable (:pr:`1636`)
- Fix UTC as default `tzinfo` for `Job` (:pr:`1696`)

Version 12.5
============
*Released 2020-03-29*

**New Features:**

- `Bot.link` gives the `t.me` link of the bot (:pr:`1770`)

**Major Changes:**

- Bot API 4.5 and 4.6 support. (:pr:`1508`, :pr:`1723`)

**Minor changes, CI improvements or bug fixes:**

- Remove legacy CI files (:pr:`1783`, :pr:`1791`)
- Update pre-commit config file (:pr:`1787`)
- Remove builtin names (:pr:`1792`)
- CI improvements (:pr:`1808`, :pr:`1848`)
- Support Python 3.8 (:pr:`1614`, :pr:`1824`)
- Use stale bot for auto closing stale issues (:pr:`1820`, :pr:`1829`, :pr:`1840`)
- Doc fixes (:pr:`1778`, :pr:`1818`)
- Fix typo in `edit_message_media` (:pr:`1779`)
- In examples, answer CallbackQueries and use `edit_message_text` shortcut (:pr:`1721`)
- Revert accidental change in vendored urllib3 (:pr:`1775`)

Version 12.4.2
==============
*Released 2020-02-10*

**Bug Fixes**

- Pass correct parse_mode to InlineResults if bot.defaults is None (:pr:`1763`)
- Make sure PP can read files that dont have bot_data (:pr:`1760`)

Version 12.4.1
==============
*Released 2020-02-08*

This is a quick release for :pr:`1744` which was accidently left out of v12.4.0 though mentioned in the
release notes.

Version 12.4.0
==============
*Released 2020-02-08*

**New features:**

- Set default values for arguments appearing repeatedly. We also have a `wiki page for the new defaults`_. (:pr:`1490`)
- Store data in ``CallbackContext.bot_data`` to access it in every callback. Also persists. (:pr:`1325`)
- ``Filters.poll`` allows only messages containing a poll (:pr:`1673`)

**Major changes:**

- ``Filters.text`` now accepts messages that start with a slash, because ``CommandHandler`` checks for ``MessageEntity.BOT_COMMAND`` since v12. This might lead to your MessageHandlers receiving more updates than before (:pr:`1680`).
- ``Filters.command`` new checks for ``MessageEntity.BOT_COMMAND`` instead of just a leading slash. Also by ``Filters.command(False)`` you can now filters for messages containing a command `anywhere` in the text (:pr:`1744`).

**Minor changes, CI improvements or bug fixes:**

- Add ``disptacher`` argument to ``Updater`` to allow passing a customized ``Dispatcher`` (:pr:`1484`)
- Add missing names for ``Filters`` (:pr:`1632`)
- Documentation fixes (:pr:`1624`, :pr:`1647`, :pr:`1669`, :pr:`1703`, :pr:`1718`, :pr:`1734`, :pr:`1740`, :pr:`1642`, :pr:`1739`, :pr:`1746`)
- CI improvements (:pr:`1716`, :pr:`1731`, :pr:`1738`, :pr:`1748`, :pr:`1749`, :pr:`1750`, :pr:`1752`)
- Fix spelling issue for ``encode_conversations_to_json`` (:pr:`1661`)
- Remove double assignement of ``Dispatcher.job_queue`` (:pr:`1698`)
- Expose dispatcher as property for ``CallbackContext`` (:pr:`1684`)
- Fix ``None`` check in ``JobQueue._put()`` (:pr:`1707`)
- Log datetimes correctly in ``JobQueue`` (:pr:`1714`)
- Fix false ``Message.link`` creation for private groups (:pr:`1741`)
- Add option ``--with-upstream-urllib3`` to `setup.py` to allow using non-vendored version (:pr:`1725`)
- Fix persistence for nested ``ConversationHandlers`` (:pr:`1679`)
- Improve handling of non-decodable server responses (:pr:`1623`)
- Fix download for files without ``file_path`` (:pr:`1591`)
- test_webhook_invalid_posts is now considered flaky and retried on failure (:pr:`1758`)

.. _`wiki page for the new defaults`: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Adding-defaults-to-your-bot

Version 12.3.0
==============
*Released 2020-01-11*

**New features:**

- `Filters.caption` allows only messages with caption (:pr:`1631`).
- Filter for exact messages/captions with new capability of `Filters.text` and `Filters.caption`. Especially useful in combination with ReplyKeyboardMarkup. (:pr:`1631`).

**Major changes:**

- Fix inconsistent handling of naive datetimes (:pr:`1506`).

**Minor changes, CI improvements or bug fixes:**

- Documentation fixes (:pr:`1558`, :pr:`1569`, :pr:`1579`, :pr:`1572`, :pr:`1566`, :pr:`1577`, :pr:`1656`).
- Add mutex protection on `ConversationHandler` (:pr:`1533`).
- Add `MAX_PHOTOSIZE_UPLOAD` constant (:pr:`1560`).
- Add args and kwargs to `Message.forward()` (:pr:`1574`).
- Transfer to GitHub Actions CI (:pr:`1555`, :pr:`1556`, :pr:`1605`, :pr:`1606`, :pr:`1607`, :pr:`1612`, :pr:`1615`, :pr:`1645`).
- Fix deprecation warning with Py3.8 by vendored urllib3 (:pr:`1618`).
- Simplify assignements for optional arguments (:pr:`1600`)
- Allow private groups for `Message.link` (:pr:`1619`).
- Fix wrong signature call for `ConversationHandler.TIMEOUT` handlers (:pr:`1653`).

Version 12.2.0
==============
*Released 2019-10-14*

**New features:**

- Nested ConversationHandlers (:pr:`1512`).

**Minor changes, CI improvments or bug fixes:**

- Fix CI failures due to non-backward compat attrs depndency (:pr:`1540`).
- travis.yaml: TEST_OFFICIAL removed from allowed_failures.
- Fix typos in examples (:pr:`1537`).
- Fix Bot.to_dict to use proper first_name (:pr:`1525`).
- Refactor ``test_commandhandler.py`` (:pr:`1408`).
- Add Python 3.8 (RC version) to Travis testing matrix (:pr:`1543`).
- test_bot.py: Add to_dict test (:pr:`1544`).
- Flake config moved into setup.cfg (:pr:`1546`).

Version 12.1.1
==============
*Released 2019-09-18*

**Hot fix release**

Fixed regression in the vendored urllib3 (:pr:`1517`).

Version 12.1.0
================
*Released 2019-09-13*

**Major changes:**

- Bot API 4.4 support (:pr:`1464`, :pr:`1510`)
- Add `get_file` method to `Animation` & `ChatPhoto`. Add, `get_small_file` & `get_big_file`
  methods to `ChatPhoto` (:pr:`1489`)
- Tools for deep linking (:pr:`1049`)

**Minor changes and/or bug fixes:**

- Documentation fixes (:pr:`1500`, :pr:`1499`)
- Improved examples (:pr:`1502`)

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
- Error Handler now handles all types of exceptions (:pr:`1485`)
- Return UTC from from_timestamp() (:pr:`1485`)

**See the wiki page at https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-12.0 for a detailed guide on how to migrate from version 11 to version 12.**

Context based callbacks (:pr:`1100`)
------------------------------------

- Use of ``pass_`` in handlers is deprecated.
- Instead use ``use_context=True`` on ``Updater`` or ``Dispatcher`` and change callback from (bot, update, others...) to (update, context).
- This also applies to error handlers ``Dispatcher.add_error_handler`` and JobQueue jobs (change (bot, job) to (context) here).
- For users with custom handlers subclassing Handler, this is mostly backwards compatible, but to use the new context based callbacks you need to implement the new collect_additional_context method.
- Passing bot to ``JobQueue.__init__`` is deprecated. Use JobQueue.set_dispatcher with a dispatcher instead.
- Dispatcher makes sure to use a single `CallbackContext` for a entire update. This means that if an update is handled by multiple handlers (by using the group argument), you can add custom arguments to the `CallbackContext` in a lower group handler and use it in higher group handler. NOTE: Never use with @run_async, see docs for more info. (:pr:`1283`)
- If you have custom handlers they will need to be updated to support the changes in this release.
- Update all examples to use context based callbacks.

Persistence (:pr:`1017`)
------------------------

- Added PicklePersistence and DictPersistence for adding persistence to your bots.
- BasePersistence can be subclassed for all your persistence needs.
- Add a new example that shows a persistent ConversationHandler bot

Handler overhaul (:pr:`1114`)
-----------------------------

- CommandHandler now only triggers on actual commands as defined by telegram servers (everything that the clients mark as a tabable link).
- PrefixHandler can be used if you need to trigger on prefixes (like all messages starting with a "/" (old CommandHandler behaviour) or even custom prefixes like "#" or "!").

Filter overhaul (:pr:`1221`)
----------------------------

- RegexHandler is deprecated and should be replaced with a MessageHandler with a regex filter.
- Use update filters to filter update types instead of arguments (message_updates, channel_post_updates and edited_updates) on the handlers.
- Completely remove allow_edited argument - it has been deprecated for a while.
- data_filters now exist which allows filters that return data into the callback function. This is how the regex filter is implemented.
- All this means that it no longer possible to use a list of filters in a handler. Use bitwise operators instead!

ConversationHandler
-------------------

- Remove ``run_async_timeout`` and ``timed_out_behavior`` arguments (:pr:`1344`)
- Replace with ``WAITING`` constant and behavior from states (:pr:`1344`)
- Only emit one warning for multiple CallbackQueryHandlers in a ConversationHandler (:pr:`1319`)
- Use warnings.warn for ConversationHandler warnings (:pr:`1343`)
- Fix unresolvable promises (:pr:`1270`)

Bug fixes & improvements
------------------------

- Handlers should be faster due to deduped logic.
- Avoid compiling compiled regex in regex filter. (:pr:`1314`)
- Add missing ``left_chat_member`` to Message.MESSAGE_TYPES (:pr:`1336`)
- Make custom timeouts actually work properly (:pr:`1330`)
- Add convenience classmethods (from_button, from_row and from_column) to InlineKeyboardMarkup
- Small typo fix in setup.py (:pr:`1306`)
- Add Conflict error (HTTP error code 409) (:pr:`1154`)
- Change MAX_CAPTION_LENGTH to 1024 (:pr:`1262`)
- Remove some unnecessary clauses (:pr:`1247`, :pr:`1239`)
- Allow filenames without dots in them when sending files (:pr:`1228`)
- Fix uploading files with unicode filenames (:pr:`1214`)
- Replace http.server with Tornado (:pr:`1191`)
- Allow SOCKSConnection to parse username and password from URL (:pr:`1211`)
- Fix for arguments in passport/data.py (:pr:`1213`)
- Improve message entity parsing by adding text_mention (:pr:`1206`)
- Documentation fixes (:pr:`1348`, :pr:`1397`, :pr:`1436`)
- Merged filters short-circuit (:pr:`1350`)
- Fix webhook listen with tornado (:pr:`1383`)
- Call task_done() on update queue after update processing finished (:pr:`1428`)
- Fix send_location() - latitude may be 0 (:pr:`1437`)
- Make MessageEntity objects comparable (:pr:`1465`)
- Add prefix to thread names (:pr:`1358`)

Buf fixes since v12.0.0b1
-------------------------

- Fix setting bot on ShippingQuery (:pr:`1355`)
- Fix _trigger_timeout() missing 1 required positional argument: 'job' (:pr:`1367`)
- Add missing message.text check in PrefixHandler check_update (:pr:`1375`)
- Make updates persist even on DispatcherHandlerStop (:pr:`1463`)
- Dispatcher force updating persistence object's chat data attribute(:pr:`1462`)

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

Fixes and updates for Telegram Passport: (:pr:`1198`)

- Fix passport decryption failing at random times
- Added support for middle names.
- Added support for translations for documents
- Add errors for translations for documents
- Added support for requesting names in the language of the user's country of residence
- Replaced the payload parameter with the new parameter nonce
- Add hash to EncryptedPassportElement

Version 11.0.0
==============
*Released 2018-08-29*

Fully support Bot API version 4.0!
(also some bugfixes :))

Telegram Passport (:pr:`1174`):

- Add full support for telegram passport.
    - New types: PassportData, PassportFile, EncryptedPassportElement, EncryptedCredentials, PassportElementError, PassportElementErrorDataField, PassportElementErrorFrontSide, PassportElementErrorReverseSide, PassportElementErrorSelfie, PassportElementErrorFile and PassportElementErrorFiles.
    - New bot method: set_passport_data_errors
    - New filter: Filters.passport_data
    - Field passport_data field on Message
    - PassportData can be easily decrypted.
    - PassportFiles are automatically decrypted if originating from decrypted PassportData.
- See new passportbot.py example for details on how to use, or go to `our telegram passport wiki page`_ for more info
- NOTE: Passport decryption requires new dependency `cryptography`.

Inputfile rework (:pr:`1184`):

- Change how Inputfile is handled internally
- This allows support for specifying the thumbnails of photos and videos using the thumb= argument in the different send\_ methods.
- Also allows Bot.send_media_group to actually finally send more than one media.
- Add thumb to Audio, Video and Videonote
- Add Bot.edit_message_media together with InputMediaAnimation, InputMediaAudio, and inputMediaDocument.

Other Bot API 4.0 changes:

- Add forusquare_type to Venue, InlineQueryResultVenue, InputVenueMessageContent, and Bot.send_venue. (:pr:`1170`)
- Add vCard support by adding vcard field to Contact, InlineQueryResultContact, InputContactMessageContent, and Bot.send_contact. (:pr:`1166`)
- Support new message entities: CASHTAG and PHONE_NUMBER. (:pr:`1179`)
    - Cashtag seems to be things like `$USD` and `$GBP`, but it seems telegram doesn't currently send them to bots.
    - Phone number also seems to have limited support for now
- Add Bot.send_animation, add width, height, and duration to Animation, and add Filters.animation. (:pr:`1172`)

Non Bot API 4.0 changes:

- Minor integer comparison fix (:pr:`1147`)
- Fix Filters.regex failing on non-text message (:pr:`1158`)
- Fix ProcessLookupError if process finishes before we kill it (:pr:`1126`)
- Add t.me links for User, Chat and Message if available and update User.mention_* (:pr:`1092`)
- Fix mention_markdown/html on py2 (:pr:`1112`)

.. _`our telegram passport wiki page`: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Telegram-Passport

Version 10.1.0
==============
*Released 2018-05-02*

Fixes changing previous behaviour:

- Add urllib3 fix for socks5h support (:pr:`1085`)
- Fix send_sticker() timeout=20 (:pr:`1088`)

Fixes:

- Add a caption_entity filter for filtering caption entities (:pr:`1068`)
- Inputfile encode filenames (:pr:`1086`)
- InputFile: Fix proper naming of file when reading from subprocess.PIPE (:pr:`1079`)
- Remove pytest-catchlog from requirements (:pr:`1099`)
- Documentation fixes (:pr:`1061`, :pr:`1078`, :pr:`1081`, :pr:`1096`)

Version 10.0.2
==============
*Released 2018-04-17*

Important fix:

- Handle utf8 decoding errors (:pr:`1076`)

New features:

- Added Filter.regex (:pr:`1028`)
- Filters for Category and file types (:pr:`1046`)
- Added video note filter (:pr:`1067`)

Fixes:

- Fix in telegram.Message (:pr:`1042`)
- Make chat_id a positional argument inside shortcut methods of Chat and User classes (:pr:`1050`)
- Make Bot.full_name return a unicode object. (:pr:`1063`)
- CommandHandler faster check (:pr:`1074`)
- Correct documentation of Dispatcher.add_handler (:pr:`1071`)
- Various small fixes to documentation.

Version 10.0.1
==============
*Released 2018-03-05*

Fixes:

- Fix conversationhandler timeout (PR :pr:`1032`)
- Add missing docs utils (PR :pr:`912`)

Version 10.0.0
==============
*Released 2018-03-02*

Non backward compatabile changes and changed defaults

- JobQueue: Remove deprecated prevent_autostart & put() (PR :pr:`1012`)
- Bot, Updater: Remove deprecated network_delay (PR :pr:`1012`)
- Remove deprecated Message.new_chat_member (PR :pr:`1012`)
- Retry bootstrap phase indefinitely (by default) on network errors (PR :pr:`1018`)

New Features

- Support v3.6 API (PR :pr:`1006`)
- User.full_name convinience property (PR :pr:`949`)
- Add `send_phone_number_to_provider` and `send_email_to_provider` arguments to send_invoice (PR :pr:`986`)
- Bot: Add shortcut methods reply_{markdown,html} (PR :pr:`827`)
- Bot: Add shortcut method reply_media_group (PR :pr:`994`)
- Added utils.helpers.effective_message_type (PR :pr:`826`)
- Bot.get_file now allows passing a file in addition to file_id (PR :pr:`963`)
- Add .get_file() to Audio, Document, PhotoSize, Sticker, Video, VideoNote and Voice (PR :pr:`963`)
- Add .send_*() methods to User and Chat (PR :pr:`963`)
- Get jobs by name (PR :pr:`1011`)
- Add Message caption html/markdown methods (PR :pr:`1013`)
- File.download_as_bytearray - new method to get a d/led file as bytearray (PR :pr:`1019`)
- File.download(): Now returns a meaningful return value (PR :pr:`1019`)
- Added conversation timeout in ConversationHandler (PR :pr:`895`)

Changes

- Store bot in PreCheckoutQuery (PR :pr:`953`)
- Updater: Issue INFO log upon received signal (PR :pr:`951`)
- JobQueue: Thread safety fixes (PR :pr:`977`)
- WebhookHandler: Fix exception thrown during error handling (PR :pr:`985`)
- Explicitly check update.effective_chat in ConversationHandler.check_update (PR :pr:`959`)
- Updater: Better handling of timeouts during get_updates (PR :pr:`1007`)
- Remove unnecessary to_dict() (PR :pr:`834`)
- CommandHandler - ignore strings in entities and "/" followed by whitespace (PR :pr:`1020`)
- Documentation & style fixes (PR :pr:`942`, PR :pr:`956`, PR :pr:`962`, PR :pr:`980`, PR :pr:`983`)

Version 9.0.0
=============
*Released 2017-12-08*

Breaking changes (possibly)

- Drop support for python 3.3 (PR :pr:`930`)

New Features

- Support Bot API 3.5 (PR :pr:`920`)

Changes

- Fix race condition in dispatcher start/stop (:pr:`887`)
- Log error trace if there is no error handler registered (:pr:`694`)
- Update examples with consistent string formatting (:pr:`870`)
- Various changes and improvements to the docs.

Version 8.1.1
=============
*Released 2017-10-15*

- Fix Commandhandler crashing on single character messages (PR :pr:`873`).

Version 8.1.0
=============
*Released 2017-10-14*

New features
- Support Bot API 3.4 (PR :pr:`865`).

Changes
- MessageHandler & RegexHandler now consider channel_updates.
- Fix command not recognized if it is directly followed by a newline (PR :pr:`869`).
- Removed Bot._message_wrapper (PR :pr:`822`).
- Unitests are now also running on AppVeyor (Windows VM).
- Various unitest improvements.
- Documentation fixes.

Version 8.0.0
=============
*Released 2017-09-01*

New features

- Fully support Bot Api 3.3 (PR :pr:`806`).
- DispatcherHandlerStop (`see docs`_).
- Regression fix for text_html & text_markdown (PR :pr:`777`).
- Added effective_attachment to message (PR :pr:`766`).

Non backward compatible changes

- Removed Botan support from the library  (PR :pr:`776`).
- Fully support Bot Api 3.3 (PR :pr:`806`).
- Remove de_json() (PR :pr:`789`).

Changes

- Sane defaults for tcp socket options on linux (PR :pr:`754`).
- Add RESTRICTED as constant to ChatMember (PR :pr:`761`).
- Add rich comparison to CallbackQuery (PR :pr:`764`).
- Fix get_game_high_scores (PR :pr:`771`).
- Warn on small con_pool_size during custom initalization of Updater (PR :pr:`793`).
- Catch exceptions in error handlerfor errors that happen during polling (PR :pr:`810`).
- For testing we switched to pytest (PR :pr:`788`).
- Lots of small improvements to our tests and documentation.

.. _`see docs`: https://docs.python-telegram-bot.org/en/v13.11/telegram.ext.dispatcher.html?highlight=Dispatcher.add_handler#telegram.ext.Dispatcher.add_handler

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
- New, simpler API for ``JobQueue`` - :pr:`484`
- Download files into file-like objects - :pr:`459`
- Use vendor ``urllib3`` to address issues with timeouts
  - The default timeout for messages is now 5 seconds. For sending media, the default timeout is now 20 seconds.
- String attributes that are not set are now ``None`` by default, instead of empty strings
- Add ``text_markdown`` and ``text_html`` properties to ``Message`` - :pr:`507`
- Add support for Socks5 proxy - :pr:`518`
- Add support for filters in ``CommandHandler`` - :pr:`536`
- Add the ability to invert (not) filters - :pr:`552`
- Add ``Filters.group`` and ``Filters.private``
- Compatibility with GAE via ``urllib3.contrib`` package - :pr:`583`
- Add equality rich comparision operators to telegram objects - :pr:`604`
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
- Introduce ``telegram.constants`` - :pr:`342`

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
