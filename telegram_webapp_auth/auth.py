"""Telegram Web App Authenticator utilities."""

import base64
import binascii
import dataclasses
import hashlib
import hmac
import json
import re
import typing
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from json import JSONDecodeError
from urllib.parse import parse_qsl

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from telegram_webapp_auth.data import PROD_PUBLIC_KEY
from telegram_webapp_auth.data import TEST_PUBLIC_KEY
from telegram_webapp_auth.data import ChatType
from telegram_webapp_auth.data import WebAppChat
from telegram_webapp_auth.data import WebAppInitData
from telegram_webapp_auth.data import WebAppUser
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError

_INTEGER_RE = re.compile(r"^\d+$")
_INIT_DATA_FIELDS = {field.name for field in dataclasses.fields(WebAppInitData)}
_KNOWN_INIT_DATA_FIELDS = _INIT_DATA_FIELDS - {"extra"}


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

    def __init__(self, secret: typing.Optional[bytes] = None) -> None:
        """Initialize the authenticator with a secret key.

        Args:
            secret: secret key generated from the Telegram Bot Token
        """
        self._secret = secret

    @staticmethod
    def __parse_init_data(data: str) -> dict[str, str]:
        """Convert init_data string into dictionary.

        Args:
            data: the query string passed by the webapp
        """
        if not data:
            raise InvalidInitDataError("Init Data cannot be empty")

        try:
            parsed_items = parse_qsl(data, keep_blank_values=True, strict_parsing=True)
        except ValueError as err:
            raise InvalidInitDataError("Cannot parse init data") from err

        parsed_data: dict[str, str] = {}
        for key, value in parsed_items:
            if not key:
                raise InvalidInitDataError("Init data contains an empty key")
            if key in parsed_data:
                raise InvalidInitDataError(f"Init data contains duplicate key: {key}")
            parsed_data[key] = value

        if not parsed_data:
            raise InvalidInitDataError("Init Data cannot be empty")

        return parsed_data

    @staticmethod
    def __parse_json(data: str, field_name: str) -> dict[str, typing.Any]:
        """Convert JSON string value from WebAppInitData to Python dictionary.

        Links:
            https://core.telegram.org/bots/webapps#webappinitdata

        Raises:
            InvalidInitDataError: if the JSON string cannot be decoded.
        """
        try:
            parsed_json = json.loads(data)
        except JSONDecodeError as err:
            raise InvalidInitDataError(f"Cannot decode {field_name} data") from err

        if not isinstance(parsed_json, dict):
            raise InvalidInitDataError(f"{field_name} data must be a JSON object")

        return parsed_json

    @staticmethod
    def __parse_int(value: typing.Optional[str], field_name: str, required: bool = True) -> typing.Optional[int]:
        """Parse an integer field from init data."""
        if value is None or value == "":
            if required:
                raise InvalidInitDataError(f"Init data does not contain {field_name}")
            return None

        if not _INTEGER_RE.match(value):
            raise InvalidInitDataError(f"Invalid {field_name}")

        return int(value)

    @staticmethod
    def __build_data_check_string(init_data: dict[str, str], excluded_keys: set[str]) -> str:
        """Build a Telegram data-check-string from parsed init data."""
        return "\n".join(
            f"{key}={value}"
            for key, value in sorted(init_data.items(), key=lambda item: item[0])
            if key not in excluded_keys
        )

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
        if self._secret is None:
            raise ValueError("Telegram bot secret is required for validate()")

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
    def _check_expiry(auth_date: int, expr_in: typing.Optional[timedelta]) -> None:
        """Check if the auth_date is present and not expired."""
        try:
            auth_dt = datetime.fromtimestamp(auth_date, tz=timezone.utc)
        except (OSError, OverflowError, ValueError) as err:
            raise InvalidInitDataError("Invalid auth_date") from err

        if expr_in is not None:
            now = datetime.now(tz=timezone.utc)
            if now - auth_dt > expr_in:
                raise ExpiredInitDataError

    @staticmethod
    def __decode_signature(val: str) -> bytes:
        """Decode a base64-encoded signature, appending padding if necessary.

        :param val: A base64-encoded string.
        :return: Decoded signature as bytes.
        """
        padded_v = val + "=" * ((4 - len(val) % 4) % 4)

        try:
            return base64.b64decode(padded_v.encode("ascii"), altchars=b"-_", validate=True)
        except (binascii.Error, UnicodeEncodeError) as err:
            raise InvalidInitDataError("Invalid signature encoding") from err

    @staticmethod
    def __make_user(data: typing.Optional[str], field_name: str) -> typing.Optional[WebAppUser]:
        """Parse a WebAppUser field from init data."""
        if not data:
            return None

        user_data = TelegramAuthenticator.__parse_json(data, field_name)
        try:
            return WebAppUser(**user_data)
        except TypeError as err:
            raise InvalidInitDataError(f"Invalid {field_name} data") from err

    @staticmethod
    def __make_chat(data: typing.Optional[str]) -> typing.Optional[WebAppChat]:
        """Parse a WebAppChat field from init data."""
        if not data:
            return None

        chat_data = TelegramAuthenticator.__parse_json(data, "chat")
        chat_type = chat_data.get("type")
        if chat_type is not None:
            try:
                chat_data["type"] = ChatType(chat_type)
            except ValueError as err:
                raise InvalidInitDataError("Invalid chat type") from err

        try:
            return WebAppChat(**chat_data)
        except TypeError as err:
            raise InvalidInitDataError("Invalid chat data") from err

    def __serialize_init_data(self, init_data_dict: typing.Dict[str, typing.Any]) -> WebAppInitData:
        """Serialize the init data dictionary into WebAppInitData object.

        Args:
            init_data_dict: the init data dictionary

        Returns:
            WebAppInitData: the serialized WebAppInitData object
        """
        auth_date = self.__parse_int(init_data_dict.get("auth_date"), "auth_date")
        can_send_after = self.__parse_int(init_data_dict.get("can_send_after"), "can_send_after", required=False)

        chat_type_raw = init_data_dict.get("chat_type")
        chat_type = None
        if chat_type_raw:
            try:
                chat_type = ChatType(chat_type_raw)
            except ValueError as err:
                raise InvalidInitDataError("Invalid chat_type") from err

        extra = {key: value for key, value in init_data_dict.items() if key not in _KNOWN_INIT_DATA_FIELDS}

        return WebAppInitData(
            auth_date=typing.cast(int, auth_date),
            hash=init_data_dict.get("hash") or None,
            signature=init_data_dict.get("signature") or None,
            query_id=init_data_dict.get("query_id") or None,
            user=self.__make_user(init_data_dict.get("user"), "user"),
            receiver=self.__make_user(init_data_dict.get("receiver"), "receiver"),
            chat=self.__make_chat(init_data_dict.get("chat")),
            chat_type=chat_type,
            chat_instance=init_data_dict.get("chat_instance") or None,
            start_param=init_data_dict.get("start_param") or None,
            can_send_after=can_send_after,
            extra=extra,
        )

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
            is_test: true if the init data was issued in Telegram test environment

        Returns:
            WebAppInitData: parsed init a data object

        Raises:
            InvalidInitDataError: if the init data is invalid
            ExpiredInitDataError: if the init data is expired
        """
        init_data_dict = self.__parse_init_data(init_data)
        data_check_string = self.__build_data_check_string(init_data_dict, excluded_keys={"hash", "signature"})
        data_check_string = f"{bot_id}:WebAppData\n{data_check_string}"

        auth_date = self.__parse_int(init_data_dict.get("auth_date"), "auth_date")
        self._check_expiry(typing.cast(int, auth_date), expr_in)

        signature = init_data_dict.get("signature") or ""
        if not signature:
            raise InvalidInitDataError("Init data does not contain signature")

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
        init_data_dict = self.__parse_init_data(init_data)
        data_check_string = self.__build_data_check_string(init_data_dict, excluded_keys={"hash"})
        hash_ = init_data_dict.get("hash") or ""
        if not hash_:
            raise InvalidInitDataError("Init data does not contain hash")

        auth_date = self.__parse_int(init_data_dict.get("auth_date"), "auth_date")
        self._check_expiry(typing.cast(int, auth_date), expr_in)

        if not self._validate(hash_, data_check_string):
            raise InvalidInitDataError("Invalid data")

        return self.__serialize_init_data(init_data_dict)
