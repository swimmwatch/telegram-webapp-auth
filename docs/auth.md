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



**Args:**
 
 - <b>`init_data`</b>:  the query string passed by the webapp 


---

<a href="../telegram_webapp_auth/auth.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `parse_user_data`

```python
parse_user_data(user_data: str) → dict
```

Convert user value from WebAppInitData to Python dictionary. 

Links:  https://core.telegram.org/bots/webapps#webappinitdata 


---

<a href="../telegram_webapp_auth/auth.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_secret_key`

```python
generate_secret_key(telegram_bot_token: str, c_str: str = 'WebAppData') → str
```

Generate "Secret key" described at Telegram documentation. 

Links:  https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app 



**Args:**
 
 - <b>`telegram_bot_token`</b>:  Telegram Bot token 
 - <b>`c_str`</b>:  Encode string 



**Returns:**
 
 - <b>`str`</b>:  Secret key 


---

<a href="../telegram_webapp_auth/auth.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `validate`

```python
validate(init_data: str, secret_key: str) → bool
```

Validates the data received from the Telegram web app, using the method from Telegram documentation. 

Links:  https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app 



**Args:**
 
 - <b>`init_data`</b>:  the query string passed by the webapp 
 - <b>`secret_key`</b>:  Secret key string 



**Returns:**
 
 - <b>`bool`</b>:  Validation result 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
