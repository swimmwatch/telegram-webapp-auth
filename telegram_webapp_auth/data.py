"""This module contains data structures used in the Telegram Web Apps API."""

import dataclasses
import enum
import typing

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

TEST_PUBLIC_KEY_STR = "40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec"
PROD_PUBLIC_KEY_STR = "e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d"

TEST_PUBLIC_KEY_BYTES = bytes.fromhex(TEST_PUBLIC_KEY_STR)
PROD_PUBLIC_KEY_BYTES = bytes.fromhex(PROD_PUBLIC_KEY_STR)

TEST_PUBLIC_KEY = Ed25519PublicKey.from_public_bytes(TEST_PUBLIC_KEY_BYTES)
PROD_PUBLIC_KEY = Ed25519PublicKey.from_public_bytes(PROD_PUBLIC_KEY_BYTES)


@dataclasses.dataclass
class WebAppUser:
    """Represents a Telegram user.

    Links:
        https://core.telegram.org/bots/webapps#webappuser
    """

    id: int
    first_name: str
    is_bot: typing.Optional[bool] = None
    last_name: typing.Optional[str] = None
    username: typing.Optional[str] = None
    language_code: typing.Optional[str] = None
    is_premium: typing.Optional[bool] = None
    added_to_attachment_menu: typing.Optional[bool] = None
    allows_write_to_pm: typing.Optional[bool] = None
    photo_url: typing.Optional[str] = None


class ChatType(str, enum.Enum):
    """Represents the type of Telegram chat."""

    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


@dataclasses.dataclass
class WebAppChat:
    """Represents a Telegram chat.

    Links:
        https://core.telegram.org/bots/webapps#webappchat
    """

    id: int
    type: ChatType
    title: str
    username: typing.Optional[str] = None
    photo_url: typing.Optional[str] = None


@dataclasses.dataclass
class WebAppInitData:
    """Represents the data that the webapp receives from Telegram.

    Links:
        https://core.telegram.org/bots/webapps#webappinitdata
    """

    auth_date: int
    hash: str
    signature: str
    query_id: typing.Optional[str] = None
    user: typing.Optional[WebAppUser] = None
    receiver: typing.Optional[WebAppUser] = None
    chat: typing.Optional[WebAppChat] = None
    chat_type: typing.Optional[ChatType] = None
    chat_instance: typing.Optional[str] = None
    start_param: typing.Optional[str] = None
    can_send_after: typing.Optional[int] = None
