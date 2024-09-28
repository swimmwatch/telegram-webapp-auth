import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import TelegramUser
from telegram_webapp_auth.auth import generate_secret_key

TEST_INIT_DATA = (
    "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladislav%22"
    "%2C%22last_name%22%3A%22Kibenko%22%2C%22username%22%3A%22vdkfrost%22%2C%22language_code%22%3A%22ru%22"
    "%2C%22is_premium%22%3Atrue%7D&auth_date=1662771648&hash=c501b71e775f74ce10e377dea85a7ea24ecd640b223ea86dfe453e0eaed2e2b2"  # noqa: E501
)
TEST_TOKEN = "5768337691:AAH5YkoiEuPk8-FZa32hStHTqXiLPtAEhx8"  # noqa: S105
TEST_SECRET = generate_secret_key(TEST_TOKEN)
TEST_USER = TelegramUser(
    id=279058397,
    first_name="Vladislav",
    is_bot=None,
    last_name="Kibenko",
    username="vdkfrost",
    language_code="ru",
    is_premium=True,
    added_to_attachment_menu=None,
    allows_write_to_pm=None,
    photo_url=None,
)


@pytest.fixture()
def test_authenticator() -> TelegramAuthenticator:
    return TelegramAuthenticator(TEST_SECRET)
