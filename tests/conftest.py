import hashlib
import hmac
import re
import typing
from datetime import datetime
from datetime import timezone
from urllib.parse import parse_qsl
from urllib.parse import urlencode

import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key

_TEST_INIT_DATA = {
    "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
    "user": (
        '{"id":279058397,"first_name":"Vladislav","last_name":"Kibenko","username":"vdkfrost",'
        '"language_code":"ru","is_premium":true}'
    ),
    "auth_date": "{auth_date}",
    "signature": "some_signature",
}
_TEST_TOKEN = "5768337691:AAH5YkoiEuPk8-FZa32hStHTqXiLPtAEhx8"  # noqa: S105
_TEST_SECRET = generate_secret_key(_TEST_TOKEN)
_DEFAULT_AUTH_DATE = datetime(2021, 1, 1, tzinfo=timezone.utc)
_HASH_REGEX = re.compile(r"hash=[^&]+")


def make_data_check_string(init_data: str) -> str:
    data_dict = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    data_check_string = "\n".join(
        f"{key}={val}" for key, val in sorted(data_dict.items(), key=lambda item: item[0]) if key != "hash"
    )
    return data_check_string


def make_hash(data_check_string: str) -> str:
    return hmac.new(_TEST_SECRET, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()


def make_init_data(
    auth_date: typing.Optional[datetime] = None,
    auth_date_value: typing.Optional[str] = None,
    extra_fields: typing.Optional[dict[str, str]] = None,
) -> str:
    if auth_date is None:
        auth_date = _DEFAULT_AUTH_DATE

    fields = _TEST_INIT_DATA.copy()
    fields["auth_date"] = auth_date_value if auth_date_value is not None else str(int(auth_date.timestamp()))
    if extra_fields:
        fields.update(extra_fields)

    init_data = urlencode(fields)
    data_check_string = make_data_check_string(init_data)
    hash_ = make_hash(data_check_string)
    if _HASH_REGEX.search(init_data):
        return _HASH_REGEX.sub(f"hash={hash_}", init_data)
    return f"{init_data}&hash={hash_}"


@pytest.fixture()
def authenticator() -> TelegramAuthenticator:
    return TelegramAuthenticator(_TEST_SECRET)
