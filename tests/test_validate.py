import json
import typing
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import freezegun
import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.data import ChatType
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
        # Test case 4: zero timedelta still enables expiry validation
        (
            timedelta(seconds=0),
            datetime(2021, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            ExpiredInitDataError,
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


def test_validate_preserves_encoded_json_values(authenticator: TelegramAuthenticator) -> None:
    photo_url = "https://example.com/avatar.svg?x=1&y=2"
    user_data = json.dumps(
        {
            "id": 1,
            "first_name": "Test",
            "photo_url": photo_url,
        },
        separators=(",", ":"),
    )

    result = authenticator.validate(make_init_data(extra_fields={"user": user_data}))

    assert result.user is not None
    assert result.user.photo_url == photo_url


@pytest.mark.parametrize(
    "test_input",
    [
        make_init_data() + "&broken",
        make_init_data() + "&query_id=duplicate",
    ],
)
def test_validate_rejects_malformed_or_duplicate_query(
    test_input: str,
    authenticator: TelegramAuthenticator,
) -> None:
    with pytest.raises(InvalidInitDataError):
        authenticator.validate(test_input)


def test_validate_rejects_missing_hash(authenticator: TelegramAuthenticator) -> None:
    test_input = make_init_data().rsplit("&hash=", maxsplit=1)[0]

    with pytest.raises(InvalidInitDataError):
        authenticator.validate(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        make_init_data(auth_date_value="not-a-timestamp"),
        "&".join(part for part in make_init_data().split("&") if not part.startswith("auth_date=")),
    ],
)
def test_validate_rejects_invalid_auth_date(
    test_input: str,
    authenticator: TelegramAuthenticator,
) -> None:
    with pytest.raises(InvalidInitDataError):
        authenticator.validate(test_input)


@pytest.mark.parametrize("user_data", ["{", "[]"])
def test_validate_rejects_invalid_user_json(
    user_data: str,
    authenticator: TelegramAuthenticator,
) -> None:
    test_input = make_init_data(extra_fields={"user": user_data})

    with pytest.raises(InvalidInitDataError):
        authenticator.validate(test_input)


def test_validate_serializes_runtime_types_and_extra(authenticator: TelegramAuthenticator) -> None:
    test_input = make_init_data(
        extra_fields={
            "can_send_after": "30",
            "chat_type": "sender",
            "future_field": "future_value",
        },
    )

    result = authenticator.validate(test_input)

    assert result.auth_date == 1609459200
    assert result.can_send_after == 30
    assert result.chat_type is ChatType.SENDER
    assert result.extra == {"future_field": "future_value"}


def test_validate_requires_secret() -> None:
    authenticator = TelegramAuthenticator()

    with pytest.raises(ValueError, match="secret is required"):
        authenticator.validate(make_init_data())
