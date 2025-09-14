class Field:
    """The base class for all field types."""
    def __init__(self, primary_key=False, default=None):
        self.primary_key = primary_key
        self.default = default


class IntegerField(Field):
    """Represents an integer field in the database."""
    pass


class TextField(Field):
    """Represents a text field in the database."""
    pass


class BooleanField(Field):
    """Represents a boolean field in the database."""
    def __init__(self, primary_key=False, default=False):
        # Booleans should default to False unless specified otherwise.
        super().__init__(primary_key=primary_key, default=default)
