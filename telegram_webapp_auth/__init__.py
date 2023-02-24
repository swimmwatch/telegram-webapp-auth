import hashlib
import hmac
import typing
from urllib.parse import unquote


def parse_init_data(init_data: str) -> typing.Dict:
    """
    Convert init_data string into dictionary.

    :param init_data: the query string passed by the webapp
    """
    return dict(param.split("=") for param in init_data.split("&"))


def _extract_hash_value(init_data: str) -> str:
    return parse_init_data(init_data)["hash"]


def generate_secret_key(telegram_bot_token: str, c_str: str = "WebAppData") -> str:
    """
    Generate "Secret key" described at:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    :param telegram_bot_token: Telegram Bot token
    :return: Secret key
    """
    c_str_enc = c_str.encode()
    token_enc = telegram_bot_token.encode()
    return hmac.new(token_enc, c_str_enc, digestmod=hashlib.sha256).hexdigest()


def validate(init_data: str, secret_key: str) -> bool:
    """
    Validates the data received from the Telegram web app, using the
    method documented here:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    :param init_data: the query string passed by the webapp
    :param secret_key: Secret key string
    :return: Validation result
    """
    hash_ = _extract_hash_value(init_data)
    unquote_init_data = unquote(init_data)
    init_data = sorted(
        [chunk.split("=") for chunk in unquote_init_data.split("&") if chunk[: len("hash=")] != "hash="],
        key=lambda x: x[0],
    )
    init_data = "\n".join([f"{key}={val}" for key, val in init_data])
    init_data_enc = init_data.encode()
    secret_key_enc = secret_key.encode()
    data_check = hmac.new(init_data_enc, secret_key_enc, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(hash_, data_check)


__all__ = ["validate", "generate_secret_key", "parse_init_data"]
