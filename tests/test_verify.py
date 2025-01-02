import typing
from datetime import UTC
from datetime import datetime
from datetime import timedelta

import freezegun
import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import TelegramUser
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError

from .conftest import TEST_USER
from .conftest import make_init_data


@pytest.mark.parametrize(
    "test_input,expected_err,expected_res",
    [
        # Test case 1: invalid format (semicolon added)
        (
            make_init_data() + ";",
            InvalidInitDataError,
            None,
        ),
        # Test case 2: valid input data
        (
            make_init_data(),
            None,
            TEST_USER,
        ),
    ],
)
def test_parse(
    test_input: str,
    expected_err: typing.Optional[typing.Type[Exception]],
    expected_res: typing.Optional[TelegramUser],
    authenticator: TelegramAuthenticator,
) -> None:
    if expected_err:
        with pytest.raises(expected_err):
            authenticator.verify_token(test_input)
    else:
        result = authenticator.verify_token(test_input)
        assert result == expected_res


@pytest.mark.parametrize(
    "expr_in,now,auth_date,expected_err",
    [
        # Test case 1: valid input data
        (
            None,
            None,
            None,
            None,
        ),
        # Test case 2: expired on 1 second
        (
            timedelta(seconds=1),
            datetime(2021, 1, 1, 0, 0, 2, tzinfo=UTC),
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=UTC),
            ExpiredInitDataError,
        ),
        # Test case 3: not expired
        (
            timedelta(seconds=10),
            datetime(2021, 1, 1, 0, 0, 2, tzinfo=UTC),
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=UTC),
            None,
        ),
    ],
)
def test_parse_expire(
    authenticator: TelegramAuthenticator,
    expr_in: typing.Optional[timedelta],
    now: typing.Optional[datetime],
    auth_date: typing.Optional[datetime],
    expected_err: typing.Optional[typing.Type[Exception]],
) -> None:
    if not now:
        now = datetime.now(tz=UTC)

    test_input = make_init_data(auth_date)

    with freezegun.freeze_time(now):
        if expected_err:
            with pytest.raises(expected_err):
                authenticator.verify_token(test_input, expr_in)
        else:
            authenticator.verify_token(test_input, expr_in)
