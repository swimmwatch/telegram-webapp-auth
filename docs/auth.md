<!-- markdownlint-disable -->

<a href="../telegram_webapp_auth/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `auth`





---

<a href="../telegram_webapp_auth/auth.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `parse_init_data`

```python
parse_init_data(init_data: str) → Dict
```

Convert init_data string into dictionary. 

:param init_data: the query string passed by the webapp 


---

<a href="../telegram_webapp_auth/auth.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `parse_user_data`

```python
parse_user_data(user_data: str) → dict
```

Convert user value from WebAppInitData to Python dictionary. https://core.telegram.org/bots/webapps#webappinitdata 


---

<a href="../telegram_webapp_auth/auth.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_secret_key`

```python
generate_secret_key(telegram_bot_token: str, c_str: str = 'WebAppData') → str
```

Generate "Secret key" described at: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app 

:param telegram_bot_token: Telegram Bot token :return: Secret key 


---

<a href="../telegram_webapp_auth/auth.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `validate`

```python
validate(init_data: str, secret_key: str) → bool
```

Validates the data received from the Telegram web app, using the method documented here: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app 

:param init_data: the query string passed by the webapp :param secret_key: Secret key string :return: Validation result 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
