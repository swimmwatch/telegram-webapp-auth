import hashlib
import hmac
import json
import typing
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from json import JSONDecodeError
from urllib.parse import unquote

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from telegram_webapp_auth.data import WebAppChat
from telegram_webapp_auth.data import WebAppInitData
from telegram_webapp_auth.data import WebAppUser
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError


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
    def __init__(self, secret: bytes) -> None:
        self._secret = secret

    @staticmethod
    def _parse_init_data(data: str) -> dict:
        """Convert init_data string into dictionary.

        Args:
            data: the query string passed by the webapp
        """
        if not data:
            raise InvalidInitDataError("Init Data cannot be empty")

        return dict(param.split("=") for param in data.split("&"))

    @staticmethod
    def _parse_json(data: str) -> dict:
        """Convert JSON string value from WebAppInitData to Python dictionary.

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

    @staticmethod
    def _ed25519_verify(
        public_key: Ed25519PublicKey,
        signature: bytes,
        message: bytes,
    ) -> bool:
        """Verify the signature of the message using the public key.

        Args:
            public_key: public key
            signature: signature
            message: original message in bytes format

        Returns:
            bool: True if the signature is valid, False otherwise
        """

        try:
            public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False

    def validate(
        self,
        init_data: str,
        expr_in: typing.Optional[timedelta] = None,
    ) -> WebAppInitData:
        """Validates the data received via the Mini App. Returns a parsed init data object if is valid.

        Links:
            https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

        Args:
            init_data: init data from mini app
            expr_in: time delta to check if the token is expired

        Returns:
            WebAppInitData: parsed init a data object

        Raises:
            InvalidInitDataError: if the init data is invalid
            ExpiredInitDataError: if the init data is expired
        """
        init_data = unquote(init_data)
        init_data_dict = self._parse_init_data(init_data)
        data_check_string = "\n".join(
            f"{key}={val}" for key, val in sorted(init_data_dict.items(), key=lambda item: item[0]) if key != "hash"
        )
        hash_ = init_data_dict.get("hash")
        if not hash_:
            raise InvalidInitDataError("Init data does not contain hash")

        hash_ = hash_.strip()

        if not self._validate(hash_, data_check_string):
            raise InvalidInitDataError("Invalid token")

        auth_date = init_data_dict.get("auth_date")
        if not auth_date:
            raise InvalidInitDataError("Init data does not contain auth_date")

        try:
            auth_dt = datetime.fromtimestamp(float(auth_date), tz=timezone.utc)
        except ValueError:
            raise InvalidInitDataError("Invalid auth_date")

        if expr_in:
            now = datetime.now(tz=timezone.utc)
            if now - auth_dt > expr_in:
                raise ExpiredInitDataError

        user_data = init_data_dict.get("user")
        if user_data:
            user_data = self._parse_json(user_data)

        chat_data = init_data_dict.get("chat")
        if chat_data:
            chat_data = self._parse_json(chat_data)

        receiver_data = init_data_dict.get("receiver")
        if receiver_data:
            receiver_data = self._parse_json(receiver_data)

        data = init_data_dict | {
            "user": WebAppUser(**user_data) if user_data else None,
            "receiver": WebAppUser(**receiver_data) if receiver_data else None,
            "chat": WebAppChat(**chat_data) if chat_data else None,
        }
        return WebAppInitData(**data)
