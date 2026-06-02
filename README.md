# telegram-webapp-auth

<!-- markdownlint-disable -->
![telegram-webapp-auth](https://socialify.git.ci/swimmwatch/telegram-webapp-auth/image?description=1&font=Raleway&language=1&name=1&owner=1&pattern=Brick%20Wall&theme=Dark)

<div align="center">
  <p>
    <a href="https://github.com/telegram-mini-apps-dev/awesome-telegram-mini-apps">
      <img src="https://awesome.re/mentioned-badge.svg" alt="Mentioned in Awesome Telegram Mini Apps">
    </a>
    <a href="https://pypi.org/project/telegram-webapp-auth">
        <img src="https://img.shields.io/pypi/v/telegram-webapp-auth.svg" alt="PyPI">
    </a>
    <a href="https://pypi.org/project/telegram-webapp-auth">
        <img src="https://img.shields.io/pypi/pyversions/telegram-webapp-auth" alt="Supported Python Versions">
    </a>
    <br/>
    <a href="https://github.com/swimmwatch/telegram-webapp-auth/blob/dev/LICENSE">
        <img src="https://img.shields.io/github/license/swimmwatch/telegram-webapp-auth" alt="License">
    </a>
    <a href="https://github.com/ambv/black">
        <img src="https://img.shields.io/badge/code%20style-black-black" alt="Code style">
    </a>
    <a href="https://github.com/pycqa/flake8">
        <img src="https://img.shields.io/badge/lint-flake8-black" alt="Linter">
    </a>
    <a href="https://github.com/python/mypy">
        <img src="https://img.shields.io/badge/type%20checker-mypy-black" alt="Type checker">
    </a>
    <br/>
    <a href="https://github.com/swimmwatch/telegram-webapp-auth/actions/workflows/python-check.yml">
        <img src="https://github.com/swimmwatch/telegram-webapp-auth/actions/workflows/python-check.yml/badge.svg" alt="Tests">
    </a>
    <a href="https://codecov.io/github/swimmwatch/telegram-webapp-auth" target="_blank">
        <img src="https://codecov.io/github/swimmwatch/telegram-webapp-auth/graph/badge.svg?token=M638BMDY5V" alt="Coverage">
    </a>
    <a href="https://github.com/swimmwatch/telegram-webapp-auth/actions/workflows/docs.yml">
        <img src="https://github.com/swimmwatch/telegram-webapp-auth/actions/workflows/docs.yml/badge.svg" alt="Docs">
    </a>
  </p>
</div>
<!-- markdownlint-enable -->

`telegram-webapp-auth` validates Telegram Mini App `initData` in Python.

It implements Telegram's official Mini Apps authentication algorithms, supports both bot-token and third-party validation flows, and returns typed dataclasses for users, chats, and init data.

## Features

- Bot-token validation with `TelegramAuthenticator.validate()`
- Third-party Ed25519 validation with `TelegramAuthenticator.validate_third_party()`
- Optional expiry checks with `expr_in`
- Typed `WebAppInitData`, `WebAppUser`, and `WebAppChat` results, with unknown top-level fields preserved
- Python 3.10+ support
- Lightweight runtime dependency set

## Installation

```bash
pip install telegram-webapp-auth
# or
poetry add telegram-webapp-auth
# or
uv add telegram-webapp-auth
```

## Quick Start

```python
from datetime import timedelta

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError

secret_key = generate_secret_key("123456:ABC-DEF")
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

## Documentation

Read the full documentation at [swimmwatch.github.io/telegram-webapp-auth](https://swimmwatch.github.io/telegram-webapp-auth/).

Useful starting points:

- [Installation](https://swimmwatch.github.io/telegram-webapp-auth/guide/install/)
- [Quick start](https://swimmwatch.github.io/telegram-webapp-auth/guide/quick-start/)
- [Third-party validation](https://swimmwatch.github.io/telegram-webapp-auth/guide/third-party/)
- [API reference](https://swimmwatch.github.io/telegram-webapp-auth/references/auth/)

## Maintenance And Security

This project is in maintenance mode and accepts bug fixes. Please report security issues privately; see [SECURITY.md](SECURITY.md).

## License

`telegram-webapp-auth` is licensed under the [MIT License](https://github.com/swimmwatch/telegram-webapp-auth/blob/dev/LICENSE).
