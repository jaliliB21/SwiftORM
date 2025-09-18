class DriverError(Exception):
    """Base exception for all driver-related errors."""
    pass


class ORMError(Exception):
    """Base exception for all ORM-related errors."""
    pass


class ValidationError(ORMError):
    """Raised when data fails validation checks."""
    pass


class IntegrityError(ORMError):
    """Raised when a database integrity constraint is violated (e.g., UNIQUE)."""
    pass


class ObjectNotFound(ORMError):
    """Raised by `get()` when the requested object does not exist."""
    pass


class MultipleObjectsReturned(ORMError):
    """Raised by `get()` when more than one object is returned."""
    pass