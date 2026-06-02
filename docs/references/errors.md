# Exceptions

The `telegram_webapp_auth.errors` module defines the public exception hierarchy raised by validation.

Catch `InvalidInitDataError` and `ExpiredInitDataError` at your HTTP boundary and translate them into your framework's authorization response.

::: telegram_webapp_auth.errors
