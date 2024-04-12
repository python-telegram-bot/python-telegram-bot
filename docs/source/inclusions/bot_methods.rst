.. raw:: html

   <hr style="height:2px;border-width:0;color:gray;background-color:gray">
   <p>Since this class has a large number of methods and attributes, below you can find a quick overview.

   </p>
   <details>
   <summary>Sending Messages</summary>

.. list-table::
        :align: left
        :widths: 1 4

        * - :meth:`~telegram.Bot.send_animation`
          - Used for sending animations
        * - :meth:`~telegram.Bot.send_audio`
          - Used for sending audio files
        * - :meth:`~telegram.Bot.send_chat_action`
          - Used for sending chat actions
        * - :meth:`~telegram.Bot.send_contact`
          - Used for sending contacts
        * - :meth:`~telegram.Bot.send_dice`
          - Used for sending dice messages
        * - :meth:`~telegram.Bot.send_document`
          - Used for sending documents
        * - :meth:`~telegram.Bot.send_game`
          - Used for sending a game
        * - :meth:`~telegram.Bot.send_invoice`
          - Used for sending an invoice
        * - :meth:`~telegram.Bot.send_location`
          - Used for sending location
        * - :meth:`~telegram.Bot.send_media_group`
          - Used for sending media grouped together
        * - :meth:`~telegram.Bot.send_message`
          - Used for sending text messages
        * - :meth:`~telegram.Bot.send_photo`
          - Used for sending photos
        * - :meth:`~telegram.Bot.send_poll`
          - Used for sending polls
        * - :meth:`~telegram.Bot.send_sticker`
          - Used for sending stickers
        * - :meth:`~telegram.Bot.send_venue`
          - Used for sending venue locations.
        * - :meth:`~telegram.Bot.send_video`
          - Used for sending videos
        * - :meth:`~telegram.Bot.send_video_note`
          - Used for sending video notes
        * - :meth:`~telegram.Bot.send_voice`
          - Used for sending voice messages
        * - :meth:`~telegram.Bot.copy_message`
          - Used for copying the contents of an arbitrary message
        * - :meth:`~telegram.Bot.copy_messages`
          - Used for copying the contents of an multiple arbitrary messages
        * - :meth:`~telegram.Bot.forward_message`
          - Used for forwarding messages
        * - :meth:`~telegram.Bot.forward_messages`
          - Used for forwarding multiple messages at once

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Updating Messages</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.answer_callback_query`
      - Used for answering the callback query
    * - :meth:`~telegram.Bot.answer_inline_query`
      - Used for answering the inline query
    * - :meth:`~telegram.Bot.answer_pre_checkout_query`
      - Used for answering a pre checkout query
    * - :meth:`~telegram.Bot.answer_shipping_query`
      - Used for answering a shipping query
    * - :meth:`~telegram.Bot.answer_web_app_query`
      - Used for answering a web app query
    * - :meth:`~telegram.Bot.delete_message`
      - Used for deleting messages.
    * - :meth:`~telegram.Bot.delete_messages`
      - Used for deleting multiple messages as once.
    * - :meth:`~telegram.Bot.edit_message_caption`
      - Used for editing captions
    * - :meth:`~telegram.Bot.edit_message_media`
      - Used for editing the media on messages
    * - :meth:`~telegram.Bot.edit_message_live_location`
      - Used for editing the location in live location messages
    * - :meth:`~telegram.Bot.edit_message_reply_markup`
      - Used for editing the reply markup on messages
    * - :meth:`~telegram.Bot.edit_message_text`
      - Used for editing text messages
    * - :meth:`~telegram.Bot.stop_poll`
      - Used for stopping the running poll
    * - :meth:`~telegram.Bot.set_message_reaction`
      - Used for setting reactions on messages

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Chat Moderation and information</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.approve_chat_join_request`
      - Used for approving a chat join request
    * - :meth:`~telegram.Bot.decline_chat_join_request`
      - Used for declining a chat join request
    * - :meth:`~telegram.Bot.ban_chat_member`
      - Used for banning a member from the chat
    * - :meth:`~telegram.Bot.unban_chat_member`
      - Used for unbanning a member from the chat
    * - :meth:`~telegram.Bot.ban_chat_sender_chat`
      - Used for banning a channel in a channel or supergroup
    * - :meth:`~telegram.Bot.unban_chat_sender_chat`
      - Used for unbanning a channel in a channel or supergroup
    * - :meth:`~telegram.Bot.restrict_chat_member`
      - Used for restricting a chat member
    * - :meth:`~telegram.Bot.promote_chat_member`
      - Used for promoting a chat member
    * - :meth:`~telegram.Bot.set_chat_administrator_custom_title`
      - Used for assigning a custom admin title to an admin
    * - :meth:`~telegram.Bot.set_chat_permissions`
      - Used for setting the permissions of a chat
    * - :meth:`~telegram.Bot.export_chat_invite_link`
      - Used for creating a new primary invite link for a chat
    * - :meth:`~telegram.Bot.create_chat_invite_link`
      - Used for creating an additional invite link for a chat
    * - :meth:`~telegram.Bot.edit_chat_invite_link`
      - Used for editing a non-primary invite link
    * - :meth:`~telegram.Bot.revoke_chat_invite_link`
      - Used for revoking an invite link created by the bot
    * - :meth:`~telegram.Bot.set_chat_photo`
      - Used for setting a photo to a chat
    * - :meth:`~telegram.Bot.delete_chat_photo`
      - Used for deleting a chat photo
    * - :meth:`~telegram.Bot.set_chat_title`
      - Used for setting a chat title
    * - :meth:`~telegram.Bot.set_chat_description`
      - Used for setting the description of a chat
    * - :meth:`~telegram.Bot.pin_chat_message`
      - Used for pinning a message
    * - :meth:`~telegram.Bot.unpin_chat_message`
      - Used for unpinning a message
    * - :meth:`~telegram.Bot.unpin_all_chat_messages`
      - Used for unpinning all pinned chat messages
    * - :meth:`~telegram.Bot.get_business_connection`
      - Used for getting information about the business account.
    * - :meth:`~telegram.Bot.get_user_profile_photos`
      - Used for obtaining user's profile pictures
    * - :meth:`~telegram.Bot.get_chat`
      - Used for getting information about a chat
    * - :meth:`~telegram.Bot.get_chat_administrators`
      - Used for getting the list of admins in a chat
    * - :meth:`~telegram.Bot.get_chat_member_count`
      - Used for getting the number of members in a chat
    * - :meth:`~telegram.Bot.get_chat_member`
      - Used for getting a member of a chat
    * - :meth:`~telegram.Bot.get_user_chat_boosts`
      - Used for getting the list of boosts added to a chat
    * - :meth:`~telegram.Bot.leave_chat`
      - Used for leaving a chat

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Bot settings</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.set_my_commands`
      - Used for setting the list of commands
    * - :meth:`~telegram.Bot.delete_my_commands`
      - Used for deleting the list of commands
    * - :meth:`~telegram.Bot.get_my_commands`
      - Used for obtaining the list of commands
    * - :meth:`~telegram.Bot.get_my_default_administrator_rights`
      - Used for obtaining the default administrator rights for the bot
    * - :meth:`~telegram.Bot.set_my_default_administrator_rights`
      - Used for setting the default administrator rights for the bot
    * - :meth:`~telegram.Bot.get_chat_menu_button`
      - Used for obtaining the menu button of a private chat or the default menu button
    * - :meth:`~telegram.Bot.set_chat_menu_button`
      - Used for setting the menu button of a private chat or the default menu button
    * - :meth:`~telegram.Bot.set_my_description`
      - Used for setting the description of the bot
    * - :meth:`~telegram.Bot.get_my_description`
      - Used for obtaining the description of the bot
    * - :meth:`~telegram.Bot.set_my_short_description`
      - Used for setting the short description of the bot
    * - :meth:`~telegram.Bot.get_my_short_description`
      - Used for obtaining the short description of the bot
    * - :meth:`~telegram.Bot.set_my_name`
      - Used for setting the name of the bot
    * - :meth:`~telegram.Bot.get_my_name`
      - Used for obtaining the name of the bot

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Stickerset management</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.add_sticker_to_set`
      - Used for adding a sticker to a set
    * - :meth:`~telegram.Bot.delete_sticker_from_set`
      - Used for deleting a sticker from a set
    * - :meth:`~telegram.Bot.create_new_sticker_set`
      - Used for creating a new sticker set
    * - :meth:`~telegram.Bot.delete_sticker_set`
      - Used for deleting a sticker set made by a bot
    * - :meth:`~telegram.Bot.set_chat_sticker_set`
      - Used for setting a sticker set of a chat
    * - :meth:`~telegram.Bot.delete_chat_sticker_set`
      - Used for deleting the set sticker set of a chat
    * - :meth:`~telegram.Bot.replace_sticker_in_set`
      - Used for replacing a sticker in a set
    * - :meth:`~telegram.Bot.set_sticker_position_in_set`
      - Used for moving a sticker's position in the set
    * - :meth:`~telegram.Bot.set_sticker_set_title`
      - Used for setting the title of a sticker set
    * - :meth:`~telegram.Bot.set_sticker_emoji_list`
      - Used for setting the emoji list of a sticker
    * - :meth:`~telegram.Bot.set_sticker_keywords`
      - Used for setting the keywords of a sticker
    * - :meth:`~telegram.Bot.set_sticker_mask_position`
      - Used for setting the mask position of a mask sticker
    * - :meth:`~telegram.Bot.set_sticker_set_thumbnail`
      - Used for setting the thumbnail of a sticker set
    * - :meth:`~telegram.Bot.set_custom_emoji_sticker_set_thumbnail`
      - Used for setting the thumbnail of a custom emoji sticker set
    * - :meth:`~telegram.Bot.get_sticker_set`
      - Used for getting a sticker set
    * - :meth:`~telegram.Bot.upload_sticker_file`
      - Used for uploading a sticker file
    * - :meth:`~telegram.Bot.get_custom_emoji_stickers`
      - Used for getting custom emoji files based on their IDs

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Games</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.get_game_high_scores`
      - Used for getting the game high scores
    * - :meth:`~telegram.Bot.set_game_score`
      - Used for setting the game score

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Getting updates</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.get_updates`
      - Used for getting updates using long polling
    * - :meth:`~telegram.Bot.get_webhook_info`
      - Used for getting current webhook status
    * - :meth:`~telegram.Bot.set_webhook`
      - Used for setting a webhook to receive updates
    * - :meth:`~telegram.Bot.delete_webhook`
      - Used for removing webhook integration

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Forum topic management</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.close_forum_topic`
      - Used for closing a forum topic
    * - :meth:`~telegram.Bot.close_general_forum_topic`
      - Used for closing the general forum topic
    * - :meth:`~telegram.Bot.create_forum_topic`
      - Used to create a topic
    * - :meth:`~telegram.Bot.delete_forum_topic`
      - Used for deleting a forum topic
    * - :meth:`~telegram.Bot.edit_forum_topic`
      - Used to edit a topic
    * - :meth:`~telegram.Bot.edit_general_forum_topic`
      - Used to edit the general topic
    * - :meth:`~telegram.Bot.get_forum_topic_icon_stickers`
      - Used to get custom emojis to use as topic icons
    * - :meth:`~telegram.Bot.hide_general_forum_topic`
      - Used to hide the general topic
    * - :meth:`~telegram.Bot.unhide_general_forum_topic`
      - Used to unhide the general topic
    * - :meth:`~telegram.Bot.reopen_forum_topic`
      - Used to reopen a topic
    * - :meth:`~telegram.Bot.reopen_general_forum_topic`
      - Used to reopen the general topic
    * - :meth:`~telegram.Bot.unpin_all_forum_topic_messages`
      - Used to unpin all messages in a forum topic
    * - :meth:`~telegram.Bot.unpin_all_general_forum_topic_messages`
      - Used to unpin all messages in the general forum topic

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Miscellaneous</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`~telegram.Bot.create_invoice_link`
      - Used to generate an HTTP link for an invoice
    * - :meth:`~telegram.Bot.close`
      - Used for closing server instance when switching to another local server
    * - :meth:`~telegram.Bot.log_out`
      - Used for logging out from cloud Bot API server
    * - :meth:`~telegram.Bot.get_file`
      - Used for getting basic info about a file
    * - :meth:`~telegram.Bot.get_me`
      - Used for getting basic information about the bot

.. raw:: html

   </details>
   <br>

.. raw:: html

   <details>
   <summary>Properties</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :attr:`~telegram.Bot.base_file_url`
      - Telegram Bot API file URL
    * - :attr:`~telegram.Bot.base_url`
      - Telegram Bot API service URL
    * - :attr:`~telegram.Bot.bot`
      - The user instance of the bot as returned by :meth:`~telegram.Bot.get_me`
    * - :attr:`~telegram.Bot.can_join_groups`
      - Whether the bot can join groups
    * - :attr:`~telegram.Bot.can_read_all_group_messages`
      - Whether the bot can read all incoming group messages
    * - :attr:`~telegram.Bot.id`
      - The user id of the bot
    * - :attr:`~telegram.Bot.name`
      - The username of the bot, with leading ``@``
    * - :attr:`~telegram.Bot.first_name`
      - The first name of the bot
    * - :attr:`~telegram.Bot.last_name`
      - The last name of the bot
    * - :attr:`~telegram.Bot.local_mode`
      - Whether the bot is running in local mode
    * - :attr:`~telegram.Bot.username`
      - The username of the bot, without leading ``@``
    * - :attr:`~telegram.Bot.link`
      - The t.me link of the bot
    * - :attr:`~telegram.Bot.private_key`
      - Deserialized private key for decryption of telegram passport data
    * - :attr:`~telegram.Bot.supports_inline_queries`
      - Whether the bot supports inline queries
    * - :attr:`~telegram.Bot.token`
      - Bot's unique authentication token

.. raw:: html

   </details>
   <br>
   <hr style="height:2px;border-width:0;color:gray;background-color:gray">
