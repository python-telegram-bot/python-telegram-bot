.. raw:: html

   <hr><p>Since this class has a large number of methods and attributes, below you can find a quick overview.

   </p>
   <details>
   <summary>Sending Messages</summary>

.. list-table::
        :align: left
        :widths: 1 4

        * - :meth:`send_animation`
          - Used for sending animations
        * - :meth:`send_audio`
          - Used for sending audio files
        * - :meth:`send_chat_action`
          - Used for sending chat actions
        * - :meth:`send_contact`
          - Used for sending contacts
        * - :meth:`send_dice`
          - Used for sending dice messages
        * - :meth:`send_document`
          - Used for sending documents
        * - :meth:`send_game`
          - Used for sending a game
        * - :meth:`send_invoice`
          - Used for sending an invoice
        * - :meth:`send_location`
          - Used for sending location
        * - :meth:`send_media_group`
          - Used for sending media grouped together
        * - :meth:`send_message`
          - Used for sending text messages
        * - :meth:`send_photo`
          - Used for sending photos
        * - :meth:`send_poll`
          - Used for sending polls
        * - :meth:`send_sticker`
          - Used for sending stickers
        * - :meth:`send_venue`
          - Used for sending venue locations.
        * - :meth:`send_video`
          - Used for sending videos
        * - :meth:`send_video_note`
          - Used for sending video notes
        * - :meth:`send_voice`
          - Used for sending voice messages
        * - :meth:`copy_message`
          - Used for copying the contents of an arbitrary message
        * - :meth:`forward_message`
          - Used for forwarding messages

.. raw:: html

   </details>
   </hr>

.. raw:: html

   <details>
   <summary>Updating Messages</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`answer_callback_query`
      - Used for answering the callback query
    * - :meth:`answer_inline_query`
      - Used for answering the inline query
    * - :meth:`answer_pre_checkout_query`
      - Used for answering a pre checkout query
    * - :meth:`answer_shipping_query`
      - Used for answering a shipping query
    * - :meth:`edit_message_caption`
      - Used for editing captions
    * - :meth:`edit_message_media`
      - Used for editing the media on messages
    * - :meth:`edit_message_live_location`
      - Used for editing the location in live location messages
    * - :meth:`edit_message_reply_markup`
      - Used for editing the reply markup on messages
    * - :meth:`edit_message_text`
      - Used for editing text messages
    * - :meth:`stop_poll`
      - Used for stopping the running poll
    * - :meth:`delete_message`
      - Used for deleting messages.

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary>Chat Moderation and information</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`ban_chat_member`
      - Used for banning a member from the chat
    * - :meth:`unban_chat_member`
      - Used for unbanning a member from the chat
    * - :meth:`ban_chat_sender_chat`
      - Used for banning a channel in a channel or supergroup
    * - :meth:`unban_chat_sender_chat`
      - Used for unbanning a channel in a channel or supergroup
    * - :meth:`restrict_chat_member`
      - Used for restricting a chat member
    * - :meth:`promote_chat_member`
      - Used for promoting a chat member
    * - :meth:`set_chat_administrator_custom_title`
      - Used for assigning a custom admin title to an admin
    * - :meth:`set_chat_permissions`
      - Used for setting the permissions of a chat
    * - :meth:`export_chat_invite_link`
      - Used for creating a new primary invite link for a chat
    * - :meth:`create_chat_invite_link`
      - Used for creating an additional invite link for a chat
    * - :meth:`edit_chat_invite_link`
      - Used for editing a non-primary invite link
    * - :meth:`revoke_chat_invite_link`
      - Used for revoking an invite link created by the bot
    * - :meth:`approve_chat_join_request`
      - Used for approving a chat join request
    * - :meth:`decline_chat_join_request`
      - Used for declining a chat join request
    * - :meth:`set_chat_photo`
      - Used for setting a photo to a chat
    * - :meth:`delete_chat_photo`
      - Used for deleting a chat photo
    * - :meth:`set_chat_title`
      - Used for setting a chat title
    * - :meth:`set_chat_description`
      - Used for setting the description of a chat
    * - :meth:`pin_chat_message`
      - Used for pinning a message
    * - :meth:`unpin_chat_message`
      - Used for unpinning a message
    * - :meth:`unpin_all_chat_messages`
      - Used for unpinning all pinned chat messages
    * - :meth:`get_user_profile_photos`
      - Used for obtaining user's profile pictures
    * - :meth:`get_chat`
      - Used for getting information about a chat
    * - :meth:`get_chat_administrators`
      - Used for getting the list of admins in a chat
    * - :meth:`get_chat_member_count`
      - Used for getting the number of members in a chat
    * - :meth:`get_chat_member`
      - Used for getting a member of a chat
    * - :meth:`set_my_commands`
      - Used for setting the list of commands
    * - :meth:`delete_my_commands`
      - Used for deleting the list of commands
    * - :meth:`get_my_commands`
      - Used for obtaining the list of commands
    * - :meth:`leave_chat`
      - Used for leaving a chat

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary>Stickerset management</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`add_sticker_to_set`
      - Used for adding a sticker to a set
    * - :meth:`delete_sticker_from_set`
      - Used for deleting a sticker from a set
    * - :meth:`create_new_sticker_set`
      - Used for creating a new sticker set
    * - :meth:`set_chat_sticker_set`
      - Used for setting a sticker set
    * - :meth:`delete_chat_sticker_set`
      - Used for deleting the set sticker set
    * - :meth:`set_sticker_position_in_set`
      - Used for moving a sticker's position in the set
    * - :meth:`set_sticker_set_thumb`
      - Used for setting the thumbnail of a sticker set
    * - :meth:`get_sticker_set`
      - Used for getting a sticker set
    * - :meth:`upload_sticker_file`
      - Used for uploading a sticker file

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary>Games</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`get_game_high_scores`
      - Used for getting the game high scores
    * - :meth:`set_game_score`
      - Used for setting the game score

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary>Getting updates</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`get_updates`
      - Used for getting updates using long polling
    * - :meth:`get_webhook_info`
      - Used for getting current webhook status
    * - :meth:`set_webhook`
      - Used for setting a webhook to receive updates
    * - :meth:`delete_webhook`
      - Used for removing webhook integration

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary>Miscellaneous</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :meth:`close`
      - Used for closing server instance when switching to another local server
    * - :meth:`log_out`
      - Used for logging out from cloud Bot API server
    * - :meth:`get_file`
      - Used for getting basic info about a file
    * - :meth:`get_me`
      - Used for getting basic information about the bot

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary>Properties</summary>

.. list-table::
    :align: left
    :widths: 1 4

    * - :attr:`bot`
      - The user instance of the bot as returned by :meth:`get_me`
    * - :attr:`can_join_groups`
      - Whether the bot can join groups
    * - :attr:`can_read_all_group_messages`
      - Whether the bot can read all incoming group messages
    * - :attr:`id`
      - The user id of the bot
    * - :attr:`name`
      - The username of the bot, with leading ``@``
    * - :attr:`first_name`
      - The first name of the bot
    * - :attr:`last_name`
      - The last name of the bot
    * - :attr:`username`
      - The username of the bot, without leading ``@``
    * - :attr:`link`
      - The t.me link of the bot
    * - :attr:`supports_inline_queries`
      - Whether the bot supports inline queries

.. raw:: html

   </details>