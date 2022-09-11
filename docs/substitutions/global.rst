.. |toapikwargsbase| replace:: These arguments are also considered by :meth:`~telegram.TelegramObject.to_dict` and :meth:`~telegram.TelegramObject.to_json`, i.e. when passing objects to Telegram. Passing them to Telegram is however not guaranteed to work for all kinds of objects, e.g. this will fail for objects that can not directly be JSON serialized.

.. |toapikwargsarg| replace:: Arbitrary keyword arguments. Can be used to store data for which there are no dedicated attributes. |toapikwargsbase|

.. |toapikwargsattr| replace:: Optional. Arbitrary keyword arguments. Used to store data for which there are no dedicated attributes. |toapikwargsbase|