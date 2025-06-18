import typing
from datetime import timedelta

import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError

_TEST_INIT_DATA = (
    "query_id=AAH1t3EVAAAAAPW3cRVyuBgH&"
    "user=%7B%22id%22%3A359774197%2C%22first_name%22%3A%22Dmitry%22%2C%22"
    "last_name%22%3A%22Vasiliev%22%2C%22language_code%22%3A%22en%22%2C%22"
    "allows_write_to_pm%22%3Atrue%2C%22"
    "photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FaUkVEo2bVNr6G41sIB2bNwCdbkwnaVS79N41WHr_ApQ.svg%22%7D&"  # noqa: E501
    "auth_date=1736353840&"
    "signature=s72bv8J1hwJanbDqlo9TTMK6Uf4WSwQKuPKK_Q16QBhKD0hfOfoYCOpRl_d8m_8AEI1_oF-9WCJuwW1KQy5-BA&"
    "hash=c0b008672bf1edae403293e790eec42d047ac6613a5799e1939fac5eca41a397"
)
_TEST_BOT_ID = 7544535829


@pytest.mark.parametrize(
    "test_input,expected_err",
    [
        # Test case 1: invalid format (semicolon added)
        (
            ";" + _TEST_INIT_DATA,
            InvalidInitDataError,
        ),
        # Test case 2: positive case
        (
            _TEST_INIT_DATA,
            None,
        ),
    ],
)
def test_parse(
    test_input: str,
    expected_err: typing.Optional[typing.Type[Exception]],
    authenticator: TelegramAuthenticator,
) -> None:
    if expected_err:
        with pytest.raises(expected_err):
            authenticator.validate_third_party(test_input, _TEST_BOT_ID)
    else:
        authenticator.validate_third_party(test_input, _TEST_BOT_ID)


@pytest.mark.parametrize(
    "expr_in,expected_err",
    [
        # Test case 1: valid input data
        (
            None,
            None,
        ),
        # Test case 2: expired on 1 second
        (
            timedelta(seconds=1),
            ExpiredInitDataError,
        ),
        # Test case 3: not expired
        (
            timedelta(seconds=0),
            None,
        ),
    ],
)
def test_parse_expire(
    authenticator: TelegramAuthenticator,
    expr_in: typing.Optional[timedelta],
    expected_err: typing.Optional[typing.Type[Exception]],
) -> None:
    if expected_err:
        with pytest.raises(expected_err):
            authenticator.validate_third_party(_TEST_INIT_DATA, _TEST_BOT_ID, expr_in)
    else:
        authenticator.validate_third_party(_TEST_INIT_DATA, _TEST_BOT_ID, expr_in)


@pytest.mark.benchmark
def test_validate_third_party_performance(benchmark, authenticator: TelegramAuthenticator):
    benchmark.pedantic(
        authenticator.validate_third_party,
        args=(_TEST_INIT_DATA, _TEST_BOT_ID, timedelta(seconds=0)),
        rounds=100,
        iterations=10,
        warmup_rounds=10,
    )
