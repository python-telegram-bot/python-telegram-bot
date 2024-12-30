import datetime as dtm
from collections.abc import Sequence
from typing import Union

from telegram import (
    BotCommand,
    BotDescription,
    BotName,
    BotShortDescription,
    BusinessConnection,
    Chat,
    ChatAdministratorRights,
    ChatBoost,
    ChatBoostSource,
    ChatFullInfo,
    ChatInviteLink,
    ChatMember,
    File,
    ForumTopic,
    GameHighScore,
    Gift,
    Gifts,
    MenuButton,
    MessageId,
    Poll,
    PollOption,
    PreparedInlineMessage,
    SentWebAppMessage,
    StarTransaction,
    StarTransactions,
    Sticker,
    StickerSet,
    TelegramObject,
    Update,
    User,
    UserChatBoosts,
    UserProfilePhotos,
    WebhookInfo,
)
from tests.auxil.build_messages import make_message

_DUMMY_USER = User(
    id=123456, is_bot=False, first_name="Dummy", last_name="User", username="dummy_user"
)
_DUMMY_DATE = dtm.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dtm.timezone.utc)
_DUMMY_STICKER = Sticker(
    file_id="dummy_file_id",
    file_unique_id="dummy_file_unique_id",
    width=1,
    height=1,
    is_animated=False,
    is_video=False,
    type="dummy_type",
)

_PREPARED_DUMMY_OBJECTS: dict[str, object] = {
    "bool": True,
    "BotCommand": BotCommand(command="dummy_command", description="dummy_description"),
    "BotDescription": BotDescription(description="dummy_description"),
    "BotName": BotName(name="dummy_name"),
    "BotShortDescription": BotShortDescription(short_description="dummy_short_description"),
    "BusinessConnection": BusinessConnection(
        user=_DUMMY_USER,
        id="123",
        user_chat_id=123456,
        date=_DUMMY_DATE,
        can_reply=True,
        is_enabled=True,
    ),
    "Chat": Chat(id=123456, type="dummy_type"),
    "ChatAdministratorRights": ChatAdministratorRights.all_rights(),
    "ChatFullInfo": ChatFullInfo(
        id=123456,
        type="dummy_type",
        accent_color_id=1,
        max_reaction_count=1,
    ),
    "ChatInviteLink": ChatInviteLink(
        "dummy_invite_link",
        creator=_DUMMY_USER,
        is_primary=True,
        is_revoked=False,
        creates_join_request=False,
    ),
    "ChatMember": ChatMember(user=_DUMMY_USER, status="dummy_status"),
    "File": File(file_id="dummy_file_id", file_unique_id="dummy_file_unique_id"),
    "ForumTopic": ForumTopic(message_thread_id=2, name="dummy_name", icon_color=1),
    "Gifts": Gifts(gifts=[Gift(id="dummy_id", sticker=_DUMMY_STICKER, star_count=1)]),
    "GameHighScore": GameHighScore(position=1, user=_DUMMY_USER, score=1),
    "int": 123456,
    "MenuButton": MenuButton(type="dummy_type"),
    "Message": make_message("dummy_text"),
    "MessageId": MessageId(123456),
    "Poll": Poll(
        id="dummy_id",
        question="dummy_question",
        options=[PollOption(text="dummy_text", voter_count=1)],
        is_closed=False,
        is_anonymous=False,
        total_voter_count=1,
        type="dummy_type",
        allows_multiple_answers=False,
    ),
    "PreparedInlineMessage": PreparedInlineMessage(id="dummy_id", expiration_date=_DUMMY_DATE),
    "SentWebAppMessage": SentWebAppMessage(inline_message_id="dummy_inline_message_id"),
    "StarTransactions": StarTransactions(
        transactions=[StarTransaction(id="dummy_id", amount=1, date=_DUMMY_DATE)]
    ),
    "Sticker": _DUMMY_STICKER,
    "StickerSet": StickerSet(
        name="dummy_name",
        title="dummy_title",
        stickers=[_DUMMY_STICKER],
        sticker_type="dummy_type",
    ),
    "str": "dummy_string",
    "Update": Update(update_id=123456),
    "User": _DUMMY_USER,
    "UserChatBoosts": UserChatBoosts(
        boosts=[
            ChatBoost(
                boost_id="dummy_id",
                add_date=_DUMMY_DATE,
                expiration_date=_DUMMY_DATE,
                source=ChatBoostSource(source="dummy_source"),
            )
        ]
    ),
    "UserProfilePhotos": UserProfilePhotos(total_count=1, photos=[[]]),
    "WebhookInfo": WebhookInfo(
        url="dummy_url",
        has_custom_certificate=False,
        pending_update_count=1,
    ),
}


def get_dummy_object(obj_type: Union[type, str], as_tuple: bool = False) -> object:
    obj_type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
    if (return_value := _PREPARED_DUMMY_OBJECTS.get(obj_type_name)) is None:
        raise ValueError(
            f"Dummy object of type '{obj_type_name}' not found. Please add it manually."
        )

    if as_tuple:
        return (return_value,)
    return return_value


_RETURN_TYPES = Union[bool, int, str, dict[str, object]]
_RETURN_TYPE = Union[_RETURN_TYPES, tuple[_RETURN_TYPES, ...]]


def _serialize_dummy_object(obj: object) -> _RETURN_TYPE:
    if isinstance(obj, Sequence) and not isinstance(obj, str):
        return tuple(_serialize_dummy_object(item) for item in obj)
    if isinstance(obj, (str, int, bool)):
        return obj
    if isinstance(obj, TelegramObject):
        return obj.to_dict()

    raise ValueError(f"Serialization of object of type '{type(obj)}' is not supported yet.")


def get_dummy_object_json_dict(obj_type: Union[type, str], as_tuple: bool = False) -> _RETURN_TYPE:
    return _serialize_dummy_object(get_dummy_object(obj_type, as_tuple=as_tuple))
