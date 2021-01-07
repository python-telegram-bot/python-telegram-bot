<!--
Hey! You're PRing? Cool! Please have a look at the below checklist. It's here to help both you and the maintainers remember some things. For more details, please see our contribution guide.
-->

### Checklist for PRs

- [ ] Added `.. versionadded:: version`, `.. versionchanged:: version` or `.. deprecated:: version` if appropriate 
- [ ] Created new or adapted existing unit tests
- [ ] Added myself to `AUTHORS.rst` (optional)


### If the PR contains API changes (delete if not relevant)

* New classes:
    - [ ] Added `self._id_attrs` and corresponding documentation
    - [ ] `__init__` accepts `**_kwargs`
    
* Added new shortcuts:

    - [ ] At `Chat` & `User` for all methods that accept `chat/user_ad`
    - [ ] At `Message` for all methods that accept `chat_id` and `message_id`
    - [ ] For new `Message` shortcuts: Added `quote` argument if methods accepts `reply_to_message_id`
    - [ ] At `CallbackQuery` for all methods that accept either `chat_id` and `message_id` or `inline_message_id`
    
* If relevant:

    - [ ] Added new constants at `telegram.constants` and shortcuts to them as class variables
    - [ ] Added new handlers for new update types
    - [ ] Added new filters for new message (sub)types