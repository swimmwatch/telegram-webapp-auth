# FastAPI Integration

FastAPI dependencies are a good fit for Telegram Mini App authentication. Create one dependency that validates `initData` and returns the current Telegram user.

## Authentication Dependency

```python
import http
from datetime import timedelta

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key
from telegram_webapp_auth.data import WebAppUser
from telegram_webapp_auth.errors import ExpiredInitDataError
from telegram_webapp_auth.errors import InvalidInitDataError

from .config import TelegramBotSettings

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
        init_data = telegram_authenticator.validate(
            init_data=auth_cred.credentials,
            expr_in=timedelta(minutes=5),
        )
    except ExpiredInitDataError as exc:
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail="Telegram init data has expired.",
        ) from exc
    except InvalidInitDataError as exc:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Telegram init data is invalid.",
        ) from exc

    if init_data.user is None:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Telegram user data is required.",
        )

    return init_data.user
```

## Protected Route

```python
from fastapi import Depends
from fastapi import FastAPI
from pydantic import BaseModel

from telegram_webapp_auth.data import WebAppUser

from .auth import get_current_user

app = FastAPI()


class Message(BaseModel):
    text: str


@app.post("/message")
async def send_message(
    message: Message,
    user: WebAppUser = Depends(get_current_user),
):
    return {
        "telegram_user_id": user.id,
        "message": message.text,
    }
```

!!! note "Header format"

    `HTTPBase()` expects an `Authorization` header with a scheme and credentials. A common frontend format is `Authorization: TWA <initData>`. Adapt the dependency if your client sends init data in another header or request body.
