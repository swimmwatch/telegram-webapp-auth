# Telegram Web App Auth

Validate Telegram Mini App `initData` in Python with a small, typed, security-focused package.

`telegram-webapp-auth` implements the validation algorithms from the official Telegram Mini Apps documentation and returns structured dataclasses for users, chats, and init data.

!!! success "Current release: 3.2.1"

    The published package, documentation, and `master` branch are aligned for release `3.2.1`.

<div class="grid cards" markdown>

-   :material-shield-check: **Bot-token validation**

    Use `TelegramAuthenticator.validate()` when your backend owns the bot token and receives `initData` from your Mini App frontend.

-   :material-key-chain: **Third-party validation**

    Use `TelegramAuthenticator.validate_third_party()` when you only know the bot ID and need Telegram's Ed25519 signature flow.

-   :material-timer-check: **Expiry checks**

    Pass `expr_in` to reject stale init data and protect endpoints from replayed payloads.

-   :material-language-python: **Typed Python API**

    Work with `WebAppInitData`, `WebAppUser`, and `WebAppChat` objects instead of raw query strings.

</div>

## :material-download: Install

=== "pip"

    ```bash
    pip install telegram-webapp-auth
    ```

=== "Poetry"

    ```bash
    poetry add telegram-webapp-auth
    ```

=== "uv"

    ```bash
    uv add telegram-webapp-auth
    ```

## :material-rocket-launch: Quick Example

```python
from datetime import timedelta

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError

bot_token = "123456:ABC-DEF"
secret_key = generate_secret_key(bot_token)
authenticator = TelegramAuthenticator(secret_key)

try:
    init_data = authenticator.validate(
        init_data=request.headers["Authorization"],
        expr_in=timedelta(minutes=5),
    )
except ExpiredInitDataError:
    raise PermissionError("Telegram init data has expired")
except InvalidInitDataError:
    raise PermissionError("Telegram init data is invalid")

telegram_user = init_data.user
```

!!! tip "Choosing the right validator"

    Use `validate()` for the standard Mini App backend flow with your bot token.
    Use `validate_third_party()` when you validate data for third-party use with a bot ID and Telegram public key signature.

## :material-map-marker-outline: Documentation Map

- [Installation](guide/install.md) explains requirements, package managers, and environment setup.
- [Quick start](guide/quick-start.md) shows the standard bot-token validation flow.
- [Third-party validation](guide/third-party.md) explains the Ed25519 signature flow.
- [Error handling](guide/error-handling.md) covers `InvalidInitDataError`, `ExpiredInitDataError`, and expiry checks.
- [FastAPI](guide/examples/fastapi.md) and [Django](guide/examples/django.md) show framework integration patterns.
- [API reference](references/auth.md) documents the public Python API.

## :material-link: Project Links

- [GitHub repository](https://github.com/swimmwatch/telegram-webapp-auth)
- [PyPI package](https://pypi.org/project/telegram-webapp-auth/)
- [Telegram Mini Apps validation docs](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)
