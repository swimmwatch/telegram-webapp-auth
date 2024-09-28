import typing

import pytest

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import TelegramUser
from telegram_webapp_auth.errors import InvalidInitDataError

from .conftest import TEST_INIT_DATA
from .conftest import TEST_USER


@pytest.mark.parametrize(
    "test_input,expected_err,expected_res",
    [
        # Test case 1: invalid format (semicolon added)
        (TEST_INIT_DATA + ";", InvalidInitDataError, None),
        # Test case 2: valid input data
        (
            TEST_INIT_DATA,
            None,
            TEST_USER,
        ),
    ],
)
def test_parse(
    test_input: str,
    expected_err: typing.Union[Exception, None],
    expected_res: typing.Union[TelegramUser, None],
    test_authenticator: TelegramAuthenticator,
):
    if expected_err:
        with pytest.raises(InvalidInitDataError):
            test_authenticator.verify_token(test_input)
    else:
        result = test_authenticator.verify_token(test_input)
        assert result == expected_res
