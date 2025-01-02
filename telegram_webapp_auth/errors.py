class BaseTWAError(Exception):
    pass


class InvalidInitDataError(BaseTWAError):
    pass


class ExpiredInitDataError(BaseTWAError):
    pass
