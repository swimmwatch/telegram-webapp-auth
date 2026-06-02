# Data Models

Validated Telegram data is returned as dataclasses from `telegram_webapp_auth.data`.

Use these models for typed access to users, chats, and launch metadata after validation succeeds. Unknown top-level Telegram fields are preserved in `WebAppInitData.extra`.

::: telegram_webapp_auth.data
