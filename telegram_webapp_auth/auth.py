import dataclasses
import hashlib
import hmac
import json
from json import JSONDecodeError
from urllib.parse import unquote

from telegram_webapp_auth.errors import InvalidInitDataError


@dataclasses.dataclass
class TelegramUser:
    """Represents a Telegram user.

    Links:
        https://core.telegram.org/bots/webapps#webappuser
    """

    id: int
    first_name: str
    is_bot: bool | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    allows_write_to_pm: bool | None = None
    photo_url: str | None = None


def generate_secret_key(token: str) -> bytes:
    """Generates a secret key from a Telegram token.

    Links:
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

    Args:
        token: Telegram Bot Token

    Returns:
        bytes: secret key
    """
    base = "WebAppData".encode("utf-8")
    token_enc = token.encode("utf-8")
    return hmac.digest(base, token_enc, hashlib.sha256)


class TelegramAuthenticator:
    def __init__(self, secret: bytes):
        self._secret = secret

    @staticmethod
    def _parse_init_data(data: str) -> dict:
        """Convert init_data string into dictionary.

        Args:
            data: the query string passed by the webapp
        """
        return dict(param.split("=") for param in data.split("&"))

    @staticmethod
    def _parse_user_data(data: str) -> dict:
        """Convert user value from WebAppInitData to Python dictionary.

        Links:
            https://core.telegram.org/bots/webapps#webappinitdata

        Raises:
            InvalidInitDataError
        """
        try:
            return json.loads(unquote(data))
        except JSONDecodeError:
            raise InvalidInitDataError("Cannot decode init data")

    def _validate(self, hash_: str, token: str) -> bool:
        """Validates the data received from the Telegram web app, using the method from Telegram documentation.

        Links:
            https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

        Args:
            hash_: hash from init data
            token: init data from webapp

        Returns:
            bool: Validation result
        """
        token_bytes = token.encode("utf-8")
        client_hash = hmac.new(self._secret, token_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(client_hash, hash_)

    def verify_token(self, token: str) -> TelegramUser:
        """Verifies the data using the method from documentation. Returns Telegram user if data is valid.

        Links:
            https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

        Args:
            hash_: hash from init data
            token: init data from webapp

        Returns:
            TelegramUser: Telegram user if token is valid

        Raises:
            InvalidInitDataError: if the token is invalid
        """
        init_data = self._parse_init_data(token)
        token = "\n".join(
            f"{key}={val}" for key, val in sorted(init_data.items(), key=lambda item: item[0]) if key != "hash"
        )
        token = unquote(token)
        hash_ = init_data.get("hash")
        if not hash_:
            raise InvalidInitDataError("Init data does not contain hash")

        hash_ = hash_.strip()

        if not self._validate(hash_, token):
            raise InvalidInitDataError("Invalid token")

        user_data = init_data.get("user")
        if not user_data:
            raise InvalidInitDataError("Init data does not contain user")

        user_data = unquote(user_data)
        user_data = self._parse_user_data(user_data)
        return TelegramUser(**user_data)
