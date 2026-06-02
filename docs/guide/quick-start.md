# Quick Start

This guide covers the standard Telegram Mini App backend flow: your backend receives `initData`, validates it with your bot token-derived secret, and then uses the parsed Telegram user data.

## 1. Create An Authenticator

Generate a secret key from your bot token once, then reuse the authenticator in your request handlers.

```python
from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key

BOT_TOKEN = "123456:ABC-DEF"

secret_key = generate_secret_key(BOT_TOKEN)
authenticator = TelegramAuthenticator(secret_key)
```

!!! warning "Do not accept user identity without validation"

    Telegram `initData` is a signed query string. Always call `validate()` before trusting fields like `user.id`, `username`, or `auth_date`.

## 2. Validate `initData`

In most backends, the frontend sends `window.Telegram.WebApp.initData` in an `Authorization` header or request body.

```python
from datetime import timedelta

from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError


def authenticate(init_data_raw: str):
    try:
        return authenticator.validate(
            init_data=init_data_raw,
            expr_in=timedelta(minutes=5),
        )
    except ExpiredInitDataError:
        raise PermissionError("Telegram init data has expired")
    except InvalidInitDataError:
        raise PermissionError("Telegram init data is invalid")
```

## 3. Use Parsed Data

`validate()` returns `WebAppInitData`. User, receiver, and chat fields are parsed into typed dataclasses when present.

```python
init_data = authenticate(init_data_raw)

if init_data.user is None:
    raise PermissionError("Telegram user data is missing")

telegram_user_id = init_data.user.id
display_name = init_data.user.first_name
username = init_data.user.username
```

## Standard Flow Checklist

- Store the bot token in a secret manager or environment variable.
- Generate the secret key on the backend.
- Validate every protected request.
- Use `expr_in` for replay protection.
- Treat missing `user` data as an authorization failure when your endpoint requires a user.
