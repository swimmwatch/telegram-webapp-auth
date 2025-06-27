class BaseTWAError(Exception):
    """Base class for all TWA-related exceptions."""

    pass


class InvalidInitDataError(BaseTWAError):
    """Raised when the init data is invalid."""

    pass


class ExpiredInitDataError(BaseTWAError):
    """Raised when the init data has expired."""

    pass
