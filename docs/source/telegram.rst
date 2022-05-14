telegram package
================

Version Constants
-----------------

.. py:module:: telegram
.. py:attribute:: __version__

   The version of the `python-telegram-bot` library as string.
   To get detailed information about the version number, please use :data:`__version_info__` instead.

   :value: :tg-const:`telegram.__version__`
   :type: str

.. py:data:: __version_info__

   A tuple containing the five components of the version number: `major`, `minor`, `micro`, `releaselevel`, and `serial`.
   All values except `releaselevel` are integers.
   The release level is ``'alpha'``, ``'beta'``, ``'candidate'``, or ``'final'``.
   The components can also be accessed by name, so ``__version_info__[0]`` is equivalent to ``__version_info__.major`` and so on.

   .. versionadded:: 20.0

   :value: :tg-const:`telegram.__version_info__`
   :type: :class:`typing.NamedTuple`

.. py:data:: __bot_api_version__

   Shortcut for :const:`telegram.constants.BOT_API_VERSION`.

   .. versionchanged:: 20.0
      This constant was previously named ``bot_api_version``.

   :type: str

.. py:data:: __bot_api_version_info__

   Shortcut for :const:`telegram.constants.BOT_API_VERSION_INFO`.

   .. versionadded:: 20.0

   :type: :class:`typing.NamedTuple`

Available Types
---------------

.. toctree::

    telegram.animation
    telegram.audio
    telegram.bot
    telegram.botcommand
    telegram.botcommandscope
    telegram.botcommandscopedefault
    telegram.botcommandscopeallprivatechats
    telegram.botcommandscopeallgroupchats
    telegram.botcommandscopeallchatadministrators
    telegram.botcommandscopechat
    telegram.botcommandscopechatadministrators
    telegram.botcommandscopechatmember
    telegram.callbackquery
    telegram.chat
    telegram.chatadministratorrights
    telegram.chatinvitelink
    telegram.chatjoinrequest
    telegram.chatlocation
    telegram.chatmember
    telegram.chatmemberowner
    telegram.chatmemberadministrator
    telegram.chatmembermember
    telegram.chatmemberrestricted
    telegram.chatmemberleft
    telegram.chatmemberbanned
    telegram.chatmemberupdated
    telegram.chatpermissions
    telegram.chatphoto
    telegram.contact
    telegram.dice
    telegram.document
    telegram.file
    telegram.forcereply
    telegram.inlinekeyboardbutton
    telegram.inlinekeyboardmarkup
    telegram.inputfile
    telegram.inputmedia
    telegram.inputmediaanimation
    telegram.inputmediaaudio
    telegram.inputmediadocument
    telegram.inputmediaphoto
    telegram.inputmediavideo
    telegram.keyboardbutton
    telegram.keyboardbuttonpolltype
    telegram.location
    telegram.loginurl
    telegram.menubutton
    telegram.menubuttoncommands
    telegram.menubuttondefault
    telegram.menubuttonwebapp
    telegram.message
    telegram.messageautodeletetimerchanged
    telegram.messageid
    telegram.messageentity
    telegram.photosize
    telegram.poll
    telegram.pollanswer
    telegram.polloption
    telegram.proximityalerttriggered
    telegram.replykeyboardremove
    telegram.replykeyboardmarkup
    telegram.sentwebappmessage
    telegram.telegramobject
    telegram.update
    telegram.user
    telegram.userprofilephotos
    telegram.venue
    telegram.video
    telegram.videochatended
    telegram.videochatparticipantsinvited
    telegram.videochatscheduled
    telegram.videochatstarted
    telegram.videonote
    telegram.voice
    telegram.webappdata
    telegram.webappinfo
    telegram.webhookinfo

Stickers
--------

.. toctree::

    telegram.sticker
    telegram.stickerset
    telegram.maskposition

Inline Mode
-----------

.. toctree::

    telegram.inlinequery
    telegram.inlinequeryresult
    telegram.inlinequeryresultarticle
    telegram.inlinequeryresultaudio
    telegram.inlinequeryresultcachedaudio
    telegram.inlinequeryresultcacheddocument
    telegram.inlinequeryresultcachedgif
    telegram.inlinequeryresultcachedmpeg4gif
    telegram.inlinequeryresultcachedphoto
    telegram.inlinequeryresultcachedsticker
    telegram.inlinequeryresultcachedvideo
    telegram.inlinequeryresultcachedvoice
    telegram.inlinequeryresultcontact
    telegram.inlinequeryresultdocument
    telegram.inlinequeryresultgame
    telegram.inlinequeryresultgif
    telegram.inlinequeryresultlocation
    telegram.inlinequeryresultmpeg4gif
    telegram.inlinequeryresultphoto
    telegram.inlinequeryresultvenue
    telegram.inlinequeryresultvideo
    telegram.inlinequeryresultvoice
    telegram.inputmessagecontent
    telegram.inputtextmessagecontent
    telegram.inputlocationmessagecontent
    telegram.inputvenuemessagecontent
    telegram.inputcontactmessagecontent
    telegram.inputinvoicemessagecontent
    telegram.choseninlineresult

Payments
--------

.. toctree::

    telegram.labeledprice
    telegram.invoice
    telegram.shippingaddress
    telegram.orderinfo
    telegram.shippingoption
    telegram.successfulpayment
    telegram.shippingquery
    telegram.precheckoutquery

Games
-----

.. toctree::

    telegram.game
    telegram.callbackgame
    telegram.gamehighscore

Passport
--------

.. toctree::

    telegram.passportelementerror
    telegram.passportelementerrorfile
    telegram.passportelementerrorfiles
    telegram.passportelementerrorreverseside
    telegram.passportelementerrorfrontside
    telegram.passportelementerrordatafield
    telegram.passportelementerrorselfie
    telegram.passportelementerrortranslationfile
    telegram.passportelementerrortranslationfiles
    telegram.passportelementerrorunspecified
    telegram.credentials
    telegram.datacredentials
    telegram.securedata
    telegram.securevalue
    telegram.filecredentials
    telegram.iddocumentdata
    telegram.personaldetails
    telegram.residentialaddress
    telegram.passportdata
    telegram.passportfile
    telegram.encryptedpassportelement
    telegram.encryptedcredentials
