<!-- markdownlint-disable -->

<a href="../../telegram_webapp_auth/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `auth`





---

<a href="../../telegram_webapp_auth/auth.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_secret_key`

```python
generate_secret_key(token: str) → bytes
```

Generates a secret key from a Telegram token. 

Links:  https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app 



**Args:**
 
 - <b>`token`</b>:  Telegram Bot Token 



**Returns:**
 
 - <b>`bytes`</b>:  secret key 


---

<a href="../../telegram_webapp_auth/auth.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TelegramUser`
Represents a Telegram user. 

Links:  https://core.telegram.org/bots/webapps#webappuser 

<a href="../../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    id: int,
    first_name: str,
    is_bot: bool | None = None,
    last_name: str | None = None,
    username: str | None = None,
    language_code: str | None = None,
    is_premium: bool | None = None,
    added_to_attachment_menu: bool | None = None,
    allows_write_to_pm: bool | None = None,
    photo_url: str | None = None
) → None
```









---

<a href="../../telegram_webapp_auth/auth.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TelegramAuthenticator`




<a href="../../telegram_webapp_auth/auth.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(secret: bytes)
```








---

<a href="../../telegram_webapp_auth/auth.py#L93"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_token`

```python
verify_token(token: str) → TelegramUser
```

Verifies the data using the method from documentation. Returns Telegram user if data is valid. 

Links:  https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app 



**Args:**
 
 - <b>`hash_`</b>:  hash from init data 
 - <b>`token`</b>:  init data from webapp 



**Returns:**
 
 - <b>`TelegramUser`</b>:  Telegram user if token is valid 



**Raises:**
 
 - <b>`InvalidInitDataError`</b>:  if the token is invalid 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
