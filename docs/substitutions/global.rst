.. |uploadinput| replace:: To upload a file, you can either pass a :term:`file object` (e.g. ``open("filename", "rb")``), the file contents as bytes or the path of the file (as string or :class:`pathlib.Path` object). In the latter case, the file contents will either be read as bytes or the file path will be passed to Telegram, depending on the :paramref:`~telegram.Bot.local_mode` setting.

.. |uploadinputnopath| replace:: To upload a file, you can either pass a :term:`file object` (e.g. ``open("filename", "rb")``) or the file contents as bytes. If the bot is running in :paramref:`~telegram.Bot.local_mode`, passing the path of the file (as string or :class:`pathlib.Path` object) is supported as well.

.. |fileinputbase| replace:: Pass a ``file_id`` as String to send a file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload a new one.

.. |fileinput| replace:: |fileinputbase| |uploadinput|

.. |fileinputnopath| replace:: |fileinputbase| |uploadinputnopath|

.. |thumbdocstringbase| replace:: Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can't be reused and can be only uploaded as a new file.

.. |thumbdocstring| replace:: |thumbdocstringbase| |uploadinput|

.. |thumbdocstringnopath| replace:: |thumbdocstringbase| |uploadinputnopath|

.. |editreplymarkup| replace:: It is currently only possible to edit messages without :attr:`telegram.Message.reply_markup` or with inline keyboards.

.. |toapikwargsbase| replace:: These arguments are also considered by :meth:`~telegram.TelegramObject.to_dict` and :meth:`~telegram.TelegramObject.to_json`, i.e. when passing objects to Telegram. Passing them to Telegram is however not guaranteed to work for all kinds of objects, e.g. this will fail for objects that can not directly be JSON serialized.

.. |toapikwargsarg| replace:: Arbitrary keyword arguments. Can be used to store data for which there are no dedicated attributes. |toapikwargsbase|

.. |toapikwargsattr| replace:: Optional. Arbitrary keyword arguments. Used to store data for which there are no dedicated attributes. |toapikwargsbase|

.. |chat_id_channel| replace:: Unique identifier for the target chat or username of the target channel (in the format ``@channelusername``).

.. |chat_id_group| replace:: Unique identifier for the target chat or username of the target supergroup (in the format ``@supergroupusername``).

.. |message_thread_id| replace:: Unique identifier for the target message thread of the forum topic.

.. |message_thread_id_arg| replace:: Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.

.. |parse_mode| replace:: Mode for parsing entities. See :class:`telegram.constants.ParseMode` and `formatting options <https://core.telegram.org/bots/api#formatting-options>`__ for more details.

.. |allow_sending_without_reply| replace:: Pass :obj:`True`, if the message should be sent even if the specified replied-to message is not found.

.. |caption_entities| replace:: Sequence of special entities that appear in the caption, which can be specified instead of ``parse_mode``.

.. |protect_content| replace:: Protects the contents of the sent message from forwarding and saving.

.. |disable_notification| replace:: Sends the message silently. Users will receive a notification with no sound.

.. |reply_to_msg_id| replace:: If the message is a reply, ID of the original message.

.. |sequenceclassargs| replace:: |sequenceargs| The input is converted to a tuple.

.. |tupleclassattrs| replace:: This attribute is now an immutable tuple.

.. |alwaystuple| replace:: This attribute is now always a tuple, that may be empty.

.. |sequenceargs| replace:: Accepts any :class:`collections.abc.Sequence` as input instead of just a list.

.. |captionentitiesattr| replace:: Tuple of special entities that appear in the caption, which can be specified instead of ``parse_mode``.

.. |datetime_localization| replace:: The default timezone of the bot is used for localization, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is used.

.. |post_methods_note| replace:: If you implement custom logic that implies that you will **not** be using :class:`~telegram.ext.Application`'s methods :meth:`~telegram.ext.Application.run_polling` or :meth:`~telegram.ext.Application.run_webhook` to run your application (like it's done in `Custom Webhook Bot Example <https://docs.python-telegram-bot.org/en/stable/examples.customwebhookbot.html>`__), the callback you set in this method **will not be called automatically**. So instead of setting a callback with this method, you have to explicitly ``await`` the function that you want to run at this stage of your application's life (in the `example mentioned above <https://docs.python-telegram-bot.org/en/stable/examples.customwebhookbot.html>`__, that would be in ``async with application`` context manager).

.. |removed_thumb_note| replace:: Removed the deprecated argument and attribute ``thumb``.

.. |removed_thumb_url_note| replace:: Removed the deprecated argument and attribute ``thumb_url``.

.. |removed_thumb_wildcard_note| replace:: Removed the deprecated arguments and attributes ``thumb_*``.

.. |async_context_manager| replace:: Asynchronous context manager which

.. |reply_parameters| replace:: Description of the message to reply to.

.. |rtm_aswr_deprecated| replace:: replacing this argument. PTB will automatically convert this argument to that one, but you should update your code to use the new argument.

.. |keyword_only_arg| replace:: This argument is now a keyword-only argument.

.. |text_html| replace:: The return value of this property is a best-effort approach. Unfortunately, it can not be guaranteed that sending a message with the returned string will render in the same way as the original message produces the same :attr:`~telegram.Message.entities`/:attr:`~telegram.Message.caption_entities` as the original message. For example, Telegram recommends that entities of type :attr:`~telegram.MessageEntity.BLOCKQUOTE` and :attr:`~telegram.MessageEntity.PRE` *should* start and end on a new line, but does not enforce this and leaves rendering decisions up to the clients.

.. |text_markdown| replace:: |text_html| Moreover, markdown formatting is inherently less expressive than HTML, so some edge cases may not be coverable at all. For example, markdown formatting can not specify two consecutive block quotes without a blank line in between, but HTML can.

.. |reply_quote| replace:: If set to :obj:`True`, the reply is sent as an actual reply to this message. If ``reply_to_message_id`` is passed, this parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

.. |do_quote| replace:: If set to :obj:`True`, the replied message is quoted. For a dict, it must be the output of :meth:`~telegram.Message.build_reply_arguments` to specify exact ``reply_parameters``. If ``reply_to_message_id`` or ``reply_parameters`` are passed, this parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

.. |non_optional_story_argument| replace:: As of this version, this argument is now required. In accordance with our `stability policy <https://docs.python-telegram-bot.org/en/stable/stability_policy.html>`__, the signature will be kept as optional for now, though they are mandatory and an error will be raised if you don't pass it.

.. |business_id_str| replace:: Unique identifier of the business connection on behalf of which the message will be sent.
