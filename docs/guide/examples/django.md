## Using with Django
Let's create authorization middleware.

Firstly, create variables in your `settings.py`:
```python
from telegram_webapp_auth.auth import generate_secret_key

# other settings

TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')
TELEGRAM_SECRET_KEY = generate_secret_key(TELEGRAM_BOT_TOKEN)
```

Then implement middleware:

```python
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http import HttpResponse
from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import InvalidInitDataError


class TWAAuthorizationMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response
        self._telegram_authenticator = TelegramAuthenticator(settings.TELEGRAM_SECRET_KEY)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        auth_cred = request.headers.get('Authorization')

        try:
            init_data = self._telegram_authenticator.validate(auth_cred)
        except InvalidInitDataError:
            # TODO: handle error
            pass
        
        if not init_data.user:
            # TODO: handle error
            pass

        current_user = User.objects.filter(tg_id=init_data.user.id).first()
        if not current_user:
            # TODO: handle error
            pass

        request.user = current_user  # Associate current user with the request object

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
```

To use `TWAAuthorizationMiddleware`, add it to your `MIDDLEWARE` setting in `settings.py`:
```python
MIDDLEWARE = [
    # other middleware classes
    'path.to.TWAAuthorizationMiddleware',
]
```
