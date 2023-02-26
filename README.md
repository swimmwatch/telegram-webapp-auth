# telegram-webapp-auth
This Python package implements [Telegram Web authentication algorithm](https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app).

## Examples
### Using with FastAPI
Let's create some useful stuff according [OAuth2 tutorial](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/?h=auth).

File `utils.py`:
```python
from telegram_webapp_auth import parse_user_data, parse_init_data, validate
from fastapi import HTTPException, Depends
from fastapi.security.http import HTTPBase, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .config import TelegramBotSettings  # Telegram Bot configuration

telegram_authentication_schema = HTTPBase()


class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str


def verify_token(auth_cred: HTTPAuthorizationCredentials) -> TelegramUser:
    settings = TelegramBotSettings()
    init_data = auth_cred.credentials
    try:
        if validate(init_data, settings.secret_key):
            raise ValueError("Invalid hash")
    except ValueError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    init_data = parse_init_data(init_data)
    user_data = parse_user_data(init_data["user"])
    return TelegramUser.parse_obj(user_data)


def get_current_user(
    auth_cred: HTTPAuthorizationCredentials = Depends(telegram_authentication_schema)
) -> TelegramUser:
    return verify_token(auth_cred)
```

Finally, we can use it as usual.

File `app.py`:
```python
from fastapi import FastAPI, Depends

from config import TelegramBotSettings
from utils import get_current_user, TelegramUser

app = FastAPI()


@app.get("")
async def send_message(
    user: TelegramUser = Depends(get_current_user),
):
    """
    Some backend logic...
    """
    ...
```