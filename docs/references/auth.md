# Authenticator API

The `telegram_webapp_auth.auth` module contains the public validation entry points:

- `generate_secret_key()` derives the HMAC secret from a Telegram bot token.
- `TelegramAuthenticator.validate()` validates standard Mini App `initData`.
- `TelegramAuthenticator.validate_third_party()` validates Telegram's third-party Ed25519 signature flow.

::: telegram_webapp_auth.auth
