class Field:
    """The base class for all field types."""

    # We add `required` and `unique` to the base class __init__
    def __init__(self, primary_key=False, default=None, required=False, unique=False):
        self.primary_key = primary_key
        self.default = default
        self.required = required # Will translate to a NOT NULL constraint
        self.unique = unique     # Will translate to a UNIQUE constraint


class IntegerField(Field):
    """Represents an integer field in the database."""
    pass


class TextField(Field):
    """Represents a text field in the database."""
    
    # We add `max_length` specifically to the TextField
    def __init__(self, max_length=None, **kwargs):
        self.max_length = max_length # Will translate to VARCHAR(n)
        # Pass other keywords (primary_key, default, etc.) to the parent class
        super().__init__(**kwargs)


class BooleanField(Field):
    """Represents a boolean field in the database."""
    def __init__(self, primary_key=False, default=False):
        # Booleans should default to False unless specified otherwise.
        super().__init__(primary_key=primary_key, default=default)
