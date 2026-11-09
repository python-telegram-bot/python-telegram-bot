#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2026
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Meta-tests making sure that every TelegramObject subclass has deserialization tests based on
:class:`tests.auxil.deserialization.DeserializationTestBase`."""

import functools
import importlib
import inspect
from collections.abc import Iterable
from pathlib import Path
from typing import TypeVar

import telegram
from telegram import Bot, TelegramObject
from tests.auxil.deserialization import DeserializationTestBase

# TypeVar instead of PEP 695 generics: PTB still supports Python 3.11
_T = TypeVar("_T")

TESTS_DIR = Path(__file__).parent
# Test directories that don't contain tests for TelegramObject subclasses
EXCLUDED_DIRS = {"auxil", "docs", "ext", "request", "test_official", "_utils"}

# Classes whose tests have not yet been migrated to DeserializationTestBase.
# This list must only ever shrink. When you migrate a test class, remove the class from here
# TODO: Remove this list once all classes are migrated.
PENDING_MIGRATION: frozenset[type[TelegramObject]] = frozenset(
    {
        telegram.AcceptedGiftTypes,
        telegram.AffiliateInfo,
        telegram.Animation,
        telegram.Audio,
        telegram.BackgroundFill,
        telegram.BackgroundFillFreeformGradient,
        telegram.BackgroundFillGradient,
        telegram.BackgroundFillSolid,
        telegram.BackgroundType,
        telegram.BackgroundTypeChatTheme,
        telegram.BackgroundTypeFill,
        telegram.BackgroundTypePattern,
        telegram.BackgroundTypeWallpaper,
        telegram.Birthdate,
        telegram.BotAccessSettings,
        telegram.BotCommand,
        telegram.BotCommandScope,
        telegram.BotCommandScopeAllChatAdministrators,
        telegram.BotCommandScopeAllGroupChats,
        telegram.BotCommandScopeAllPrivateChats,
        telegram.BotCommandScopeChat,
        telegram.BotCommandScopeChatAdministrators,
        telegram.BotCommandScopeChatMember,
        telegram.BotCommandScopeDefault,
        telegram.BotDescription,
        telegram.BotName,
        telegram.BotShortDescription,
        telegram.BusinessBotRights,
        telegram.BusinessConnection,
        telegram.BusinessIntro,
        telegram.BusinessLocation,
        telegram.BusinessMessagesDeleted,
        telegram.BusinessOpeningHours,
        telegram.BusinessOpeningHoursInterval,
        telegram.CallbackGame,
        telegram.CallbackQuery,
        telegram.Chat,
        telegram.ChatAdministratorRights,
        telegram.ChatBackground,
        telegram.ChatBoost,
        telegram.ChatBoostAdded,
        telegram.ChatBoostRemoved,
        telegram.ChatBoostSource,
        telegram.ChatBoostSourceGiftCode,
        telegram.ChatBoostSourceGiveaway,
        telegram.ChatBoostSourcePremium,
        telegram.ChatBoostUpdated,
        telegram.ChatFullInfo,
        telegram.ChatJoinRequest,
        telegram.ChatLocation,
        telegram.ChatMember,
        telegram.ChatMemberAdministrator,
        telegram.ChatMemberLeft,
        telegram.ChatMemberMember,
        telegram.ChatMemberOwner,
        telegram.ChatMemberRestricted,
        telegram.ChatMemberUpdated,
        telegram.ChatOwnerChanged,
        telegram.ChatOwnerLeft,
        telegram.ChatPermissions,
        telegram.ChatPhoto,
        telegram.ChatShared,
        telegram.Checklist,
        telegram.ChecklistTask,
        telegram.ChecklistTasksAdded,
        telegram.ChecklistTasksDone,
        telegram.ChosenInlineResult,
        telegram.Contact,
        telegram.CopyTextButton,
        telegram.Credentials,
        telegram.DataCredentials,
        telegram.DirectMessagePriceChanged,
        telegram.DirectMessagesTopic,
        telegram.Document,
        telegram.EncryptedCredentials,
        telegram.EncryptedPassportElement,
        telegram.ExternalReplyInfo,
        telegram.File,
        telegram.FileCredentials,
        telegram.ForceReply,
        telegram.ForumTopic,
        telegram.ForumTopicClosed,
        telegram.ForumTopicCreated,
        telegram.ForumTopicEdited,
        telegram.ForumTopicReopened,
        telegram.Game,
        telegram.GameHighScore,
        telegram.GeneralForumTopicHidden,
        telegram.GeneralForumTopicUnhidden,
        telegram.Gift,
        telegram.GiftBackground,
        telegram.GiftInfo,
        telegram.Gifts,
        telegram.Giveaway,
        telegram.GiveawayCompleted,
        telegram.GiveawayCreated,
        telegram.GiveawayWinners,
        telegram.IdDocumentData,
        telegram.InaccessibleMessage,
        telegram.InlineKeyboardButton,
        telegram.InlineKeyboardMarkup,
        telegram.InlineQuery,
        telegram.InlineQueryResult,
        telegram.InlineQueryResultArticle,
        telegram.InlineQueryResultAudio,
        telegram.InlineQueryResultCachedAudio,
        telegram.InlineQueryResultCachedDocument,
        telegram.InlineQueryResultCachedGif,
        telegram.InlineQueryResultCachedMpeg4Gif,
        telegram.InlineQueryResultCachedPhoto,
        telegram.InlineQueryResultCachedSticker,
        telegram.InlineQueryResultCachedVideo,
        telegram.InlineQueryResultCachedVoice,
        telegram.InlineQueryResultContact,
        telegram.InlineQueryResultDocument,
        telegram.InlineQueryResultGame,
        telegram.InlineQueryResultGif,
        telegram.InlineQueryResultLocation,
        telegram.InlineQueryResultMpeg4Gif,
        telegram.InlineQueryResultPhoto,
        telegram.InlineQueryResultVenue,
        telegram.InlineQueryResultVideo,
        telegram.InlineQueryResultVoice,
        telegram.InlineQueryResultsButton,
        telegram.InputChecklist,
        telegram.InputChecklistTask,
        telegram.InputContactMessageContent,
        telegram.InputInvoiceMessageContent,
        telegram.InputLocationMessageContent,
        telegram.InputMedia,
        telegram.InputMediaAnimation,
        telegram.InputMediaAudio,
        telegram.InputMediaDocument,
        telegram.InputMediaLivePhoto,
        telegram.InputMediaLocation,
        telegram.InputMediaPhoto,
        telegram.InputMediaSticker,
        telegram.InputMediaVenue,
        telegram.InputMediaVideo,
        telegram.InputMessageContent,
        telegram.InputPaidMedia,
        telegram.InputPaidMediaLivePhoto,
        telegram.InputPaidMediaPhoto,
        telegram.InputPaidMediaVideo,
        telegram.InputPollOption,
        telegram.InputProfilePhoto,
        telegram.InputProfilePhotoAnimated,
        telegram.InputProfilePhotoStatic,
        telegram.InputSticker,
        telegram.InputStoryContent,
        telegram.InputStoryContentPhoto,
        telegram.InputStoryContentVideo,
        telegram.InputTextMessageContent,
        telegram.InputVenueMessageContent,
        telegram.Invoice,
        telegram.KeyboardButton,
        telegram.KeyboardButtonPollType,
        telegram.KeyboardButtonRequestChat,
        telegram.KeyboardButtonRequestManagedBot,
        telegram.KeyboardButtonRequestUsers,
        telegram.LabeledPrice,
        telegram.LinkPreviewOptions,
        telegram.LivePhoto,
        telegram.Location,
        telegram.LocationAddress,
        telegram.LoginUrl,
        telegram.ManagedBotCreated,
        telegram.ManagedBotUpdated,
        telegram.MaskPosition,
        telegram.MaybeInaccessibleMessage,
        telegram.MenuButton,
        telegram.MenuButtonCommands,
        telegram.MenuButtonDefault,
        telegram.MenuButtonWebApp,
        telegram.Message,
        telegram.MessageAutoDeleteTimerChanged,
        telegram.MessageEntity,
        telegram.MessageId,
        telegram.MessageOrigin,
        telegram.MessageOriginChannel,
        telegram.MessageOriginChat,
        telegram.MessageOriginHiddenUser,
        telegram.MessageOriginUser,
        telegram.MessageReactionCountUpdated,
        telegram.MessageReactionUpdated,
        telegram.OrderInfo,
        telegram.OwnedGift,
        telegram.OwnedGiftRegular,
        telegram.OwnedGiftUnique,
        telegram.OwnedGifts,
        telegram.PaidMedia,
        telegram.PaidMediaInfo,
        telegram.PaidMediaLivePhoto,
        telegram.PaidMediaPhoto,
        telegram.PaidMediaPreview,
        telegram.PaidMediaPurchased,
        telegram.PaidMediaVideo,
        telegram.PaidMessagePriceChanged,
        telegram.PassportData,
        telegram.PassportElementError,
        telegram.PassportElementErrorDataField,
        telegram.PassportElementErrorFile,
        telegram.PassportElementErrorFiles,
        telegram.PassportElementErrorFrontSide,
        telegram.PassportElementErrorReverseSide,
        telegram.PassportElementErrorSelfie,
        telegram.PassportElementErrorTranslationFile,
        telegram.PassportElementErrorTranslationFiles,
        telegram.PassportElementErrorUnspecified,
        telegram.PassportFile,
        telegram.PersonalDetails,
        telegram.PhotoSize,
        telegram.Poll,
        telegram.PollAnswer,
        telegram.PollMedia,
        telegram.PollOption,
        telegram.PollOptionAdded,
        telegram.PollOptionDeleted,
        telegram.PreCheckoutQuery,
        telegram.PreparedInlineMessage,
        telegram.PreparedKeyboardButton,
        telegram.ProximityAlertTriggered,
        telegram.ReactionCount,
        telegram.ReactionType,
        telegram.ReactionTypeCustomEmoji,
        telegram.ReactionTypeEmoji,
        telegram.ReactionTypePaid,
        telegram.RefundedPayment,
        telegram.ReplyKeyboardMarkup,
        telegram.ReplyKeyboardRemove,
        telegram.ReplyParameters,
        telegram.ResidentialAddress,
        telegram.RevenueWithdrawalState,
        telegram.RevenueWithdrawalStateFailed,
        telegram.RevenueWithdrawalStatePending,
        telegram.RevenueWithdrawalStateSucceeded,
        telegram.SecureData,
        telegram.SecureValue,
        telegram.SentGuestMessage,
        telegram.SentWebAppMessage,
        telegram.SharedUser,
        telegram.ShippingAddress,
        telegram.ShippingOption,
        telegram.ShippingQuery,
        telegram.StarAmount,
        telegram.StarTransaction,
        telegram.StarTransactions,
        telegram.Sticker,
        telegram.StickerSet,
        telegram.Story,
        telegram.StoryArea,
        telegram.StoryAreaPosition,
        telegram.StoryAreaType,
        telegram.StoryAreaTypeLink,
        telegram.StoryAreaTypeLocation,
        telegram.StoryAreaTypeSuggestedReaction,
        telegram.StoryAreaTypeUniqueGift,
        telegram.StoryAreaTypeWeather,
        telegram.SuccessfulPayment,
        telegram.SuggestedPostApprovalFailed,
        telegram.SuggestedPostApproved,
        telegram.SuggestedPostDeclined,
        telegram.SuggestedPostInfo,
        telegram.SuggestedPostPaid,
        telegram.SuggestedPostParameters,
        telegram.SuggestedPostPrice,
        telegram.SuggestedPostRefunded,
        telegram.SwitchInlineQueryChosenChat,
        telegram.TextQuote,
        telegram.TransactionPartner,
        telegram.TransactionPartnerAffiliateProgram,
        telegram.TransactionPartnerChat,
        telegram.TransactionPartnerFragment,
        telegram.TransactionPartnerOther,
        telegram.TransactionPartnerTelegramAds,
        telegram.TransactionPartnerTelegramApi,
        telegram.TransactionPartnerUser,
        telegram.UniqueGift,
        telegram.UniqueGiftBackdrop,
        telegram.UniqueGiftBackdropColors,
        telegram.UniqueGiftColors,
        telegram.UniqueGiftInfo,
        telegram.UniqueGiftModel,
        telegram.UniqueGiftSymbol,
        telegram.Update,
        telegram.User,
        telegram.UserChatBoosts,
        telegram.UserProfileAudios,
        telegram.UserProfilePhotos,
        telegram.UserRating,
        telegram.UsersShared,
        telegram.Venue,
        telegram.Video,
        telegram.VideoChatEnded,
        telegram.VideoChatParticipantsInvited,
        telegram.VideoChatScheduled,
        telegram.VideoChatStarted,
        telegram.VideoNote,
        telegram.VideoQuality,
        telegram.Voice,
        telegram.WebAppData,
        telegram.WebAppInfo,
        telegram.WebhookInfo,
        telegram.WriteAccessAllowed,
    }
)


def _import_test_modules() -> None:
    for path in sorted(TESTS_DIR.rglob("test_*.py")):
        relative = path.relative_to(TESTS_DIR)
        if relative.parts[0] in EXCLUDED_DIRS:
            continue
        importlib.import_module(".".join(("tests", *relative.with_suffix("").parts)))


def _all_subclasses(cls: type[_T]) -> set[type[_T]]:
    subclasses = set(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses |= _all_subclasses(subclass)
    return subclasses


@functools.cache
def _test_classes() -> frozenset[type[DeserializationTestBase]]:
    _import_test_modules()
    return frozenset(
        cls for cls in _all_subclasses(DeserializationTestBase) if cls.__name__.startswith("Test")
    )


def _tested_classes() -> set[type[TelegramObject]]:
    return {cls.de_json_class for cls in _test_classes()}


def _telegram_object_classes() -> set[type[TelegramObject]]:
    return {
        cls
        for name in telegram.__all__
        if inspect.isclass(cls := getattr(telegram, name))
        and issubclass(cls, TelegramObject)
        and cls not in (TelegramObject, Bot)
    }


def _names(classes: Iterable[type]) -> list[str]:
    return sorted(cls.__name__ for cls in classes)


def test_test_classes_are_concrete():
    """pytest silently skips abstract classes, so a test class that forgets to implement an
    abstract method would not run any of its tests."""
    for cls in _test_classes():
        assert not inspect.isabstract(cls), (
            f"{cls.__module__}.{cls.__qualname__} doesn't implement "
            f"{sorted(cls.__abstractmethods__)}, so pytest won't collect any of its tests"
        )
        assert isinstance(getattr(cls, "de_json_class", None), type), (
            f"{cls.__module__}.{cls.__qualname__} must set `de_json_class`"
        )


def test_all_telegram_objects_have_deserialization_tests():
    missing = _telegram_object_classes() - _tested_classes() - PENDING_MIGRATION
    assert not missing, (
        f"The classes {_names(missing)} have no test class based on DeserializationTestBase"
    )


def test_pending_list_is_up_to_date():
    stale = PENDING_MIGRATION & _tested_classes()
    assert not stale, f"Please remove {_names(stale)} from PENDING_MIGRATION, they are migrated"
