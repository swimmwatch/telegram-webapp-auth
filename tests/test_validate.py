import typing
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import freezegun
import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError

from .conftest import make_init_data


@pytest.mark.parametrize(
    "test_input,expected_err",
    [
        # Test case 1: invalid format (semicolon added)
        (
            make_init_data() + ";",
            InvalidInitDataError,
        ),
        # Test case 2: valid input data
        (
            make_init_data(),
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
            authenticator.validate(test_input)
    else:
        authenticator.validate(test_input)


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
            datetime(2021, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            ExpiredInitDataError,
        ),
        # Test case 3: not expired
        (
            timedelta(seconds=10),
            datetime(2021, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
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
        now = datetime.now(tz=timezone.utc)

    test_input = make_init_data(auth_date)

    with freezegun.freeze_time(now):
        if expected_err:
            with pytest.raises(expected_err):
                authenticator.validate(test_input, expr_in)
        else:
            authenticator.validate(test_input, expr_in)


@pytest.mark.benchmark
def test_validate_performance(benchmark, authenticator: TelegramAuthenticator):
    test_input = make_init_data()
    benchmark.pedantic(
        authenticator.validate,
        args=(test_input,),
        rounds=100,
        iterations=10,
        warmup_rounds=10,
    )
