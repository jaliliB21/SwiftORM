from abc import ABC, abstractmethod
from .fields import Field


class ModelMetaclass(type):
    """
    A metaclass that transforms a user-defined model class.
    It inspects the class definition, finds all `Field` instances,
    and stores them in a `_fields` dictionary.
    """
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            # Don't apply the logic to the base Model class itself.
            return super().__new__(cls, name, bases, attrs)

        # Store the table name, defaulting to the lowercase class name.
        table_name = attrs.get('__tablename__', name.lower())
        attrs['__tablename__'] = table_name

        # Find all attributes that are instances of Field.
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        
        attrs['_fields'] = fields
        
        # Remove the field definitions from the class attributes
        # so they don't interfere with instance attributes.
        for key in fields:
            del attrs[key]
            
        # Create the new class with the modified attributes.
        return super().__new__(cls, name, bases, attrs)



# The Model class now inherits from ABC to become an abstract class.
class Model(ABC, metaclass=ModelMetaclass):
    """
    The base class for all user-defined models.
    It now defines an abstract interface for database operations.
    """
    def __init__(self, **kwargs):
        # The __init__ method remains the same.
        for key, value in kwargs.items():
            if key in self._fields:
                setattr(self, key, value)
            else:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __repr__(self):
        # The __repr__ method remains the same.
        attrs_str = ', '.join(f'{key}={getattr(self, key, None)}' for key in self._fields)
        return f"<{type(self).__name__}: {attrs_str}>"

    @abstractmethod
    async def save(self):
        """
        Saves the current instance to the database (creates if new, updates if exists).
        This method must be implemented by a subclass that is connected to a database engine.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        """
        Deletes the current instance from the database.
        This method must be implemented by a subclass.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def create(cls, **kwargs):
        """
        Creates a new instance, saves it to the database, and returns the instance.
        This method must be implemented by a subclass.
        """
        raise NotImplementedError
