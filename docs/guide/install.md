# :material-package-variant-closed: Installation

`telegram-webapp-auth` supports Python 3.10 and newer. It has one runtime dependency: `cryptography`, which is used for Telegram's Ed25519 third-party validation flow.

!!! success "Current release"

    Install `telegram-webapp-auth` `3.2.1` for the latest published package and documentation.

## :material-list-status: Requirements

- Python 3.10+
- A Telegram bot token for the standard Mini App backend flow
- A Telegram bot ID for third-party validation

!!! note "Keep bot tokens on the backend"

    Never send your bot token to a browser, Mini App frontend, mobile client, log stream, or analytics tool. Use the token only on trusted backend infrastructure.

## :material-package-down: Install The Package

=== "pip"

    ```bash
    python -m pip install --upgrade telegram-webapp-auth
    ```

=== "Poetry"

    ```bash
    poetry add telegram-webapp-auth
    ```

=== "uv"

    ```bash
    uv add telegram-webapp-auth
    ```

## :material-test-tube: Create A Clean Environment

For a new project, use a virtual environment before installing dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install telegram-webapp-auth
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## :material-check-decagram: Verify The Installation

```python
from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key

secret_key = generate_secret_key("123456:ABC-DEF")
authenticator = TelegramAuthenticator(secret_key)
```

The package is ready when this snippet imports and creates an authenticator without errors.

## :material-arrow-right-thin-circle-outline: Next Steps

- Continue with the [quick start](quick-start.md) for the standard bot-token flow.
- Read [third-party validation](third-party.md) if you need Telegram public-key validation.
- Add robust [error handling](error-handling.md) before exposing protected endpoints.
