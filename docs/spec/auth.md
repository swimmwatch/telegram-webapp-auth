<!-- markdownlint-disable -->

<a href="../../telegram_webapp_auth/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `auth`





---

<a href="../../telegram_webapp_auth/auth.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="../../telegram_webapp_auth/auth.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TelegramUser`
Represents a Telegram user. 

Links:  https://core.telegram.org/bots/webapps#webappuser 

<a href="../../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    id: int,
    first_name: str,
    is_bot: Optional[bool] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    language_code: Optional[str] = None,
    is_premium: Optional[bool] = None,
    added_to_attachment_menu: Optional[bool] = None,
    allows_write_to_pm: Optional[bool] = None,
    photo_url: Optional[str] = None
) → None
```









---

<a href="../../telegram_webapp_auth/auth.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TelegramAuthenticator`




<a href="../../telegram_webapp_auth/auth.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(secret: bytes)
```








---

<a href="../../telegram_webapp_auth/auth.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
