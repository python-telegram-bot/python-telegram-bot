<!--
Hey! You're PRing? Cool! Please have a look at the below checklist. It's here to help both you and the maintainers to remember some aspects. Make sure to check out our contribution guide (https://github.com/python-telegram-bot/python-telegram-bot/blob/master/.github/CONTRIBUTING.rst).
-->

### Checklist for PRs

- [ ] Added `.. versionadded:: version`, `.. versionchanged:: version` or `.. deprecated:: version` to the docstrings for user facing changes (for methods/class descriptions, arguments and attributes)
- [ ] Created new or adapted existing unit tests
- [ ] Documented code changes according to the [CSI standard](https://standards.mousepawmedia.com/en/stable/csi.html)
- [ ] Added myself alphabetically to `AUTHORS.rst` (optional)
- [ ] Added new classes & modules to the docs and all suitable `__all__` s


### If the PR contains API changes (otherwise, you can delete this passage)

* New classes:
    - [ ] Added `self._id_attrs` and corresponding documentation
    - [ ] `__init__` accepts `api_kwargs` as kw-only

* Added new shortcuts:
    - [ ] In `Chat` & `User` for all methods that accept `chat/user_id`
    - [ ] In `Message` for all methods that accept `chat_id` and `message_id`
    - [ ] For new `Message` shortcuts: Added `quote` argument if methods accepts `reply_to_message_id`
    - [ ] In `CallbackQuery` for all methods that accept either `chat_id` and `message_id` or `inline_message_id`

* If relevant:

    - [ ] Added new constants at `telegram.constants` and shortcuts to them as class variables
    - [ ] Link new and existing constants in docstrings instead of hard coded number and strings
    - [ ] Add new message types to `Message.effective_attachment`
    - [ ] Added new handlers for new update types
      - [ ] Add the handlers to the warning loop in the `ConversationHandler`
    - [ ] Added new filters for new message (sub)types
    - [ ] Added or updated documentation for the changed class(es) and/or method(s)
    - [ ] Added the new method(s) to `_extbot.py`
    - [ ] Added or updated `bot_methods.rst`
    - [ ] Updated the Bot API version number in all places: `README.rst` and `README_RAW.rst` (including the badge), as well as `telegram.constants.BOT_API_VERSION_INFO`
    - [ ] Added logic for arbitrary callback data in `tg.ext.Bot` for new methods that either accept a `reply_markup` in some form or have a return type that is/contains `telegram.Message`
