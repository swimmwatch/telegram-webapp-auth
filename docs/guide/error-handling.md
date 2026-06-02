# Error Handling

Validation should fail closed: if init data is invalid, expired, incomplete, or malformed, reject the request.

## Exceptions

`telegram-webapp-auth` raises two public validation exceptions:

| Exception | Meaning | Typical response |
| --- | --- | --- |
| `InvalidInitDataError` | The init data is missing, malformed, or has an invalid signature/hash. | `403 Forbidden` |
| `ExpiredInitDataError` | The init data is valid but older than the configured `expr_in`. | `401 Unauthorized` or `403 Forbidden` |

Both exceptions inherit from `BaseTWAError`.

## Recommended Pattern

```python
from datetime import timedelta

from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError


def validate_request(init_data_raw: str):
    try:
        return authenticator.validate(
            init_data=init_data_raw,
            expr_in=timedelta(minutes=5),
        )
    except ExpiredInitDataError as exc:
        raise PermissionError("Telegram init data has expired") from exc
    except InvalidInitDataError as exc:
        raise PermissionError("Telegram init data is invalid") from exc
```

!!! tip "Choose a short expiry window"

    Telegram includes `auth_date` in init data. Passing `expr_in` lets your backend reject old payloads and reduces replay risk.

## User Data May Be Optional

Telegram init data can contain different fields depending on launch context. If your endpoint requires a user, check it explicitly after validation:

```python
init_data = validate_request(init_data_raw)

if init_data.user is None:
    raise PermissionError("Telegram user data is required")
```

## Logging

Log validation failures with care:

- Do not log raw `initData`; it can contain personally identifiable data.
- Do not log bot tokens or generated secret keys.
- Prefer structured logs with request IDs and high-level failure reasons.
