<!-- markdownlint-disable -->

<a href="../../telegram_webapp_auth/data.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `data`




**Global Variables**
---------------
- **dataclasses**
- **TEST_PUBLIC_KEY_STR**
- **PROD_PUBLIC_KEY_STR**
- **TEST_PUBLIC_KEY_BYTES**
- **PROD_PUBLIC_KEY_BYTES**


---

<a href="../../telegram_webapp_auth/data.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WebAppUser`
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

<a href="../../telegram_webapp_auth/data.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChatType`








---

<a href="../../telegram_webapp_auth/data.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WebAppChat`
Represents a Telegram chat. 

Links:  https://core.telegram.org/bots/webapps#webappchat 

<a href="../../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    id: int,
    type: ChatType,
    title: str,
    username: Optional[str] = None,
    photo_url: Optional[str] = None
) → None
```









---

<a href="../../telegram_webapp_auth/data.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WebAppInitData`
Represents the data that the webapp receives from Telegram. 

Links:  https://core.telegram.org/bots/webapps#webappinitdata 

<a href="../../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    query_id: str,
    auth_date: int,
    hash: str,
    signature: str,
    user: Optional[WebAppUser] = None,
    receiver: Optional[WebAppUser] = None,
    chat: Optional[WebAppChat] = None,
    chat_type: Optional[ChatType] = None,
    chat_instance: Optional[str] = None,
    start_param: Optional[str] = None,
    can_send_after: Optional[int] = None
) → None
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
