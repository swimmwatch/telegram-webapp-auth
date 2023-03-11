import hashlib
import hmac
import json
import typing
from urllib.parse import unquote


def parse_init_data(init_data: str) -> typing.Dict:
    """Convert init_data string into dictionary.

    Args:
        init_data: the query string passed by the webapp
    """
    return dict(param.split("=") for param in init_data.split("&"))


def parse_user_data(user_data: str) -> dict:
    """Convert user value from WebAppInitData to Python dictionary.

    Links:
        https://core.telegram.org/bots/webapps#webappinitdata
    """
    return json.loads(unquote(user_data))


def _extract_hash_value(init_data: str) -> str:
    return parse_init_data(init_data)["hash"]


def generate_secret_key(telegram_bot_token: str, c_str: str = "WebAppData") -> str:
    """Generate "Secret key" described at Telegram documentation.

    Links:
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    Args:
        telegram_bot_token: Telegram Bot token
        c_str: Encode string

    Returns:
        str: Secret key
    """
    c_str_enc = c_str.encode()
    token_enc = telegram_bot_token.encode()
    return hmac.new(token_enc, c_str_enc, digestmod=hashlib.sha256).hexdigest()


def validate(init_data: str, secret_key: str) -> bool:
    """Validates the data received from the Telegram web app, using the method from Telegram documentation.

    Links:
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    Args:
        init_data: the query string passed by the webapp
        secret_key: Secret key string

    Returns:
        bool: Validation result
    """
    hash_ = _extract_hash_value(init_data)
    unquote_init_data = unquote(init_data)
    sorted_init_data = sorted(
        [chunk.split("=") for chunk in unquote_init_data.split("&") if chunk[: len("hash=")] != "hash="],
        key=lambda x: x[0],
    )
    sorted_init_data_str = "\n".join([f"{key}={val}" for key, val in sorted_init_data])
    init_data_enc = sorted_init_data_str.encode()
    secret_key_enc = secret_key.encode()
    data_check = hmac.new(init_data_enc, secret_key_enc, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(hash_, data_check)
