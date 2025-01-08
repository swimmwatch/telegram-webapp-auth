## Using with FastAPI
Let's create some useful stuff according to [OAuth2 tutorial](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/?h=auth).

File `auth.py`:

```python
import http

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import WebAppUser
from telegram_webapp_auth.auth import generate_secret_key
from telegram_webapp_auth.errors import InvalidInitDataError

from .config import TelegramBotSettings  # Telegram Bot configuration

telegram_authentication_schema = HTTPBase()


def get_telegram_authenticator() -> TelegramAuthenticator:
    settings = TelegramBotSettings()
    secret_key = generate_secret_key(settings.token)
    return TelegramAuthenticator(secret_key)


def get_current_user(
    auth_cred: HTTPAuthorizationCredentials = Depends(telegram_authentication_schema),
    telegram_authenticator: TelegramAuthenticator = Depends(get_telegram_authenticator),
) -> WebAppUser:
    try:
        init_data = telegram_authenticator.validate(auth_cred.credentials)
    except InvalidInitDataError:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )
    except Exception:
        raise HTTPException(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Internal error.",
        )
    
    if init_data.user is None:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )

    return init_data.user
```

Finally, we can use it as usual.

File `app.py`:

```python
from fastapi import Depends
from fastapi import FastAPI
from pydantic import BaseModel

from telegram_webapp_auth.auth import WebAppUser

from .auth import get_current_user

app = FastAPI()


class Message(BaseModel):
    text: str


@app.post("/message")
async def send_message(
    message: Message,
    user: WebAppUser = Depends(get_current_user),
):
    """
    Some logic...
    """
    ...
```
