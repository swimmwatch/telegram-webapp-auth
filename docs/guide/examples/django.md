# Django Integration

For Django applications, validate Telegram init data in middleware or in a dedicated authentication helper before resolving the current user.

## Settings

Generate the Telegram secret key from an environment-provided bot token:

```python
from telegram_webapp_auth.auth import generate_secret_key

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")
TELEGRAM_SECRET_KEY = generate_secret_key(TELEGRAM_BOT_TOKEN)
```

## Middleware

```python
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http import HttpResponse

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError


class TelegramWebAppAuthMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response
        self.authenticator = TelegramAuthenticator(settings.TELEGRAM_SECRET_KEY)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise PermissionDenied("Authorization header is required")

        try:
            init_data = self.authenticator.validate(
                init_data=auth_header,
                expr_in=timedelta(minutes=5),
            )
        except ExpiredInitDataError as exc:
            raise PermissionDenied("Telegram init data has expired") from exc
        except InvalidInitDataError as exc:
            raise PermissionDenied("Telegram init data is invalid") from exc

        if init_data.user is None:
            raise PermissionDenied("Telegram user data is required")

        user_model = get_user_model()
        request.user = user_model.objects.filter(tg_id=init_data.user.id).first()
        if request.user is None:
            raise PermissionDenied("Telegram user is not registered")

        return self.get_response(request)
```

## Enable Middleware

Add the middleware to `settings.py`:

```python
MIDDLEWARE = [
    # Other middleware classes...
    "path.to.TelegramWebAppAuthMiddleware",
]
```

!!! tip "Keep authentication boundaries explicit"

    Middleware is convenient for apps where every route is Telegram-protected. If only a few views need Telegram auth, use a decorator or per-view helper instead.
