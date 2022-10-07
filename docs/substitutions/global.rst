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
