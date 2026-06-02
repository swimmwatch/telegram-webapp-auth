# Third-Party Validation

Telegram also supports validating Mini App data without a bot token. This flow uses Telegram's Ed25519 public keys and the bot ID.

Use `validate_third_party()` when your service validates data for a bot it does not own, or when sharing the bot token with the validating service is not acceptable.

## Validate With A Bot ID

```python
from datetime import timedelta

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import InvalidInitDataError

authenticator = TelegramAuthenticator(secret=b"")

try:
    init_data = authenticator.validate_third_party(
        init_data=init_data_raw,
        bot_id=7544535829,
        expr_in=timedelta(minutes=5),
    )
except InvalidInitDataError:
    raise PermissionError("Telegram init data is invalid")
```

!!! info "The secret is unused in this flow"

    `TelegramAuthenticator` still requires a `secret` argument because the same class also supports bot-token validation. For `validate_third_party()`, the secret is not used.

## Test Environment

Set `is_test=True` when the init data was issued in Telegram's test environment:

```python
init_data = authenticator.validate_third_party(
    init_data=init_data_raw,
    bot_id=7544535829,
    expr_in=timedelta(minutes=5),
    is_test=True,
)
```

## When To Use Each Method

| Method | Requires | Best for |
| --- | --- | --- |
| `validate()` | Bot token-derived secret | Your own Mini App backend |
| `validate_third_party()` | Bot ID and Telegram public key signature | Services that should not know the bot token |

For the algorithm details, see Telegram's [third-party validation documentation](https://core.telegram.org/bots/webapps#validating-data-for-third-party-use).
