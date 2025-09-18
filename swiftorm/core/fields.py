from . import exceptions


class Field:
    """The base class for all field types."""

    # We add `required` and `unique` to the base class __init__
    def __init__(self, primary_key=False, default=None, required=False, unique=False):
        self.primary_key = primary_key
        self.default = default
        self.required = required # Will translate to a NOT NULL constraint
        self.unique = unique     # Will translate to a UNIQUE constraint

    def validate(self, value):
        """
        A base validation method. Can be overridden by subclasses.
        By default, it does nothing.
        """
        pass


class IntegerField(Field):
    """Represents an integer field in the database."""

    def validate(self, value):
        """Ensures the provided value is an integer."""
        super().validate(value)
        if not isinstance(value, int):
            raise exceptions.ValidationError(f"Value must be an integer, but got {type(value).__name__}.")



class TextField(Field):
    """Represents a text field in the database."""
    
    # We add `max_length` specifically to the TextField
    def __init__(self, max_length=None, **kwargs):
        self.max_length = max_length # Will translate to VARCHAR(n)
        # Pass other keywords (primary_key, default, etc.) to the parent class
        super().__init__(**kwargs)

    def validate(self, value):
        """Ensures the provided value is a string and respects max_length."""
        super().validate(value)
        if not isinstance(value, str):
            raise exceptions.ValidationError(f"Value must be a string, but got {type(value).__name__}.")
        
        # This check for max_length already exists in the Model's validate,
        # but having it here makes the Field class more self-contained.
        if self.max_length is not None and len(value) > self.max_length:
            raise exceptions.ValidationError(f"Value exceeds max length of {self.max_length}.")


class BooleanField(Field):
    """Represents a boolean field in the database."""

    def __init__(self, primary_key=False, default=False):
        # Booleans should default to False unless specified otherwise.
        super().__init__(primary_key=primary_key, default=default)

    def validate(self, value):
        """Ensures the provided value is a boolean."""
        super().validate(value)
        if not isinstance(value, bool):
            raise exceptions.ValidationError(f"Value must be a boolean, but got {type(value).__name__}.")
