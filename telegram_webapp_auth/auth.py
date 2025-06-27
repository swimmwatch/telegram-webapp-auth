"""Telegram Web App Authenticator utilities."""

import base64
import hashlib
import hmac
import json
import typing
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from json import JSONDecodeError
from urllib.parse import parse_qs
from urllib.parse import unquote

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from telegram_webapp_auth.data import PROD_PUBLIC_KEY
from telegram_webapp_auth.data import TEST_PUBLIC_KEY
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
    """Telegram Web App Authenticator."""

    def __init__(self, secret: bytes) -> None:
        """Initialize the authenticator with a secret key.

        Args:
            secret: secret key generated from the Telegram Bot Token
        """
        self._secret = secret

    @staticmethod
    def __parse_init_data(data: str) -> dict:
        """Convert init_data string into dictionary.

        Args:
            data: the query string passed by the webapp
        """
        if not data:
            raise InvalidInitDataError("Init Data cannot be empty")

        parsed_data = parse_qs(data)
        return {key: value[0] for key, value in parsed_data.items()}

    @staticmethod
    def __parse_json(data: str) -> dict:
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

    def _validate(self, hash_: str, init_data: str) -> bool:
        """Validates the data received from the Telegram web app, using the method from Telegram documentation.

        Links:
            https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

        Args:
            hash_: hash from init data
            init_data: init data from webapp

        Returns:
            bool: Validation result
        """
        init_data_bytes = init_data.encode("utf-8")
        client_hash = hmac.new(self._secret, init_data_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(client_hash, hash_)

    @staticmethod
    def __ed25519_verify(
        public_key: Ed25519PublicKey,
        signature: bytes,
        message: bytes,
    ) -> bool:
        """Verify the Ed25519 signature of the message using the public key.

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

    @staticmethod
    def _check_expiry(auth_date: typing.Optional[str], expr_in: typing.Optional[timedelta]):
        """Check if the auth_date is present and not expired."""
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

    @staticmethod
    def __decode_signature(val: str):
        """Decode a base64-encoded signature, appending padding if necessary.

        :param val: A base64-encoded string.
        :return: Decoded signature as bytes.
        """
        # Add padding if the length is not a multiple of 4
        padded_v = val + "=" * ((4 - len(val) % 4) % 4)

        # Decode the Base64 string
        try:
            signature = base64.urlsafe_b64decode(padded_v)
            return signature
        except Exception as err:
            raise InvalidInitDataError(f"An error occurred during decoding: {err}")

    def __serialize_init_data(self, init_data_dict: typing.Dict[str, typing.Any]) -> WebAppInitData:
        """Serialize the init data dictionary into WebAppInitData object.

        Args:
            init_data_dict: the init data dictionary

        Returns:
            WebAppInitData: the serialized WebAppInitData object
        """
        user_data = init_data_dict.get("user")
        if user_data:
            user_data = self.__parse_json(user_data)
            init_data_dict["user"] = WebAppUser(**user_data)
        else:
            init_data_dict["user"] = None

        chat_data = init_data_dict.get("chat")
        if chat_data:
            chat_data = self.__parse_json(chat_data)
            init_data_dict["chat"] = WebAppChat(**chat_data)
        else:
            init_data_dict["chat"] = None

        receiver_data = init_data_dict.get("receiver")
        if receiver_data:
            receiver_data = self.__parse_json(receiver_data)
            init_data_dict["receiver"] = WebAppUser(**receiver_data)
        else:
            init_data_dict["receiver"] = None

        return WebAppInitData(**init_data_dict)

    def validate_third_party(
        self,
        init_data: str,
        bot_id: int,
        expr_in: typing.Optional[timedelta] = None,
        is_test: bool = False,
    ) -> WebAppInitData:
        """Validates the data for Third-Party Use, using the method from Telegram documentation.

        Links:
            https://core.telegram.org/bots/webapps#validating-data-for-third-party-use

        Args:
            init_data: init data from mini app
            bot_id: Telegram Bot ID
            expr_in: time delta to check if the token is expired
            is_test: true if the init data was issued in Telegram production environment

        Returns:
            WebAppInitData: parsed init a data object

        Raises:
            InvalidInitDataError: if the init data is invalid
            ExpiredInitDataError: if the init data is expired
        """
        init_data = unquote(init_data)
        init_data_dict = self.__parse_init_data(init_data)
        data_check_string = "\n".join(
            f"{key}={val}"
            for key, val in sorted(init_data_dict.items(), key=lambda item: item[0])
            if key != "hash" and key != "signature"
        )
        data_check_string = f"{bot_id}:WebAppData\n{data_check_string}"

        auth_date = init_data_dict.get("auth_date")
        self._check_expiry(auth_date, expr_in)

        signature = init_data_dict.get("signature")
        if not signature:
            raise InvalidInitDataError("Init data does not contain signature")

        signature = signature.strip()

        if is_test:
            public_key = TEST_PUBLIC_KEY
        else:
            public_key = PROD_PUBLIC_KEY

        signature_bytes = self.__decode_signature(signature)
        data_check_string_bytes = data_check_string.encode("utf-8")
        if not self.__ed25519_verify(public_key, signature_bytes, data_check_string_bytes):
            raise InvalidInitDataError("Invalid data")

        return self.__serialize_init_data(init_data_dict)

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
        init_data_dict = self.__parse_init_data(init_data)
        data_check_string = "\n".join(
            f"{key}={val}" for key, val in sorted(init_data_dict.items(), key=lambda item: item[0]) if key != "hash"
        )
        hash_ = init_data_dict.get("hash")
        if not hash_:
            raise InvalidInitDataError("Init data does not contain hash")

        auth_date = init_data_dict.get("auth_date")
        self._check_expiry(auth_date, expr_in)

        hash_ = hash_.strip()
        if not self._validate(hash_, data_check_string):
            raise InvalidInitDataError("Invalid data")

        return self.__serialize_init_data(init_data_dict)
