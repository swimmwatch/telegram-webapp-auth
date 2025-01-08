import hashlib
import hmac
import re
import typing
from datetime import datetime
from datetime import timezone
from urllib.parse import unquote

import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key

_TEST_INIT_DATA = (
    "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladislav%22"
    "%2C%22last_name%22%3A%22Kibenko%22%2C%22username%22%3A%22vdkfrost%22%2C%22language_code%22%3A%22ru%22"
    "%2C%22is_premium%22%3Atrue%7D&auth_date={auth_date}&hash=some_hash&"
    "signature=some_signature"
)
_TEST_TOKEN = "5768337691:AAH5YkoiEuPk8-FZa32hStHTqXiLPtAEhx8"  # noqa: S105
_TEST_SECRET = generate_secret_key(_TEST_TOKEN)
_HASH_REGEX = re.compile(r"hash=\w+")


def make_data_check_string(init_data: str) -> str:
    data_dict = dict(param.split("=") for param in init_data.split("&"))
    data_check_string = "\n".join(
        f"{key}={val}" for key, val in sorted(data_dict.items(), key=lambda item: item[0]) if key != "hash"
    )
    return unquote(data_check_string)


def make_hash(data_check_string: str) -> str:
    return hmac.new(_TEST_SECRET, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()


def make_init_data(auth_date: typing.Optional[datetime] = None) -> str:
    if not auth_date:
        auth_date = datetime.now(tz=timezone.utc)

    unix_time = int(auth_date.timestamp())
    init_data = _TEST_INIT_DATA.format(auth_date=unix_time)
    data_check_string = make_data_check_string(init_data)
    hash_ = make_hash(data_check_string)
    return _HASH_REGEX.sub(f"hash={hash_}", init_data)


@pytest.fixture()
def authenticator() -> TelegramAuthenticator:
    return TelegramAuthenticator(_TEST_SECRET)
