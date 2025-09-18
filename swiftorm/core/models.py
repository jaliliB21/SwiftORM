from abc import ABC, abstractmethod, ABCMeta
from .fields import Field, TextField
from . import exceptions


from .query import QuerySet # <-- Import QuerySet

# A central registry to store all defined model classes.
_model_registry = []


class ModelMetaclass(type):
    """
    The metaclass now also registers the newly created model class
    in our central `_model_registry`.
    """
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        
        # We only register classes that are not the base Model itself
        # and are not marked as abstract. This is the main addition.
        if name != "Model" and not attrs.get('__abstract__', False):
            _model_registry.append(new_class)
        
        # The rest of the logic remains the same as before, but acts on the
        # `new_class` object created at the beginning.
        if name == "Model":
            return new_class

        # --- LOGIC TO ADD `objects` MANAGER ---
        setattr(new_class, 'objects', QuerySet(model_class=new_class))
        # --- END

        table_name = attrs.get('__tablename__', name.lower())
        new_class.__tablename__ = table_name

        # Find all attributes that are instances of Field.
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        
        setattr(new_class, '_fields', fields)
        
        # Remove the field definitions from the class attributes
        # so they don't interfere with instance attributes.
        for key in fields:
            delattr(new_class, key)
            
        return new_class


# We create a new metaclass that inherits from BOTH our custom metaclass and ABC's metaclass.
class CombinedMeta(ModelMetaclass, ABCMeta):
    """A combined metaclass to resolve the conflict."""
    pass


# The Model class now inherits from ABC to become an abstract class.
class Model(ABC, metaclass=CombinedMeta):
    """
    The base class for all user-defined models.
    It now defines an abstract interface for database operations.
    """
    # This new attribute prevents the base Model itself from being registered
    # in the `_model_registry`.
    __abstract__ = True

    _engine = None

    def __init__(self, **kwargs):
        """
        Initializes a model instance.
        - Sets all defined fields with their default value or None.
        - Overwrites them with any values passed in kwargs.
        """

        # Step 1: Initialize all fields from the class's `_fields` map.
        for name, field in self._fields.items():
            setattr(self, name, field.default)

        # Step 2: Overwrite with any values the user provided.
        for key, value in kwargs.items():
            if key in self._fields:
                setattr(self, key, value)
            else:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __repr__(self):
        # The __repr__ method remains the same.
        attrs_str = ', '.join(f'{key}={getattr(self, key, None)}' for key in self._fields)
        return f"<{type(self).__name__}: {attrs_str}>"

    def validate(self):
        """
        Runs validation checks for all fields before saving.
        """
        for name, field in self._fields.items():
            value = getattr(self, name, None)
            if field.required and value is None:
                raise exceptions.ValidationError(f"Field '{name}' is required and cannot be null.")
            
            # Then, if a value exists, run the field's own type-specific validation.
            if value is not None:
                field.validate(value)

    async def save(self):
        """
        Saves the current instance to the database.
        Delegates to the engine's insert or update method.
        """
        self.validate() # <-- Run validation before saving
        if self.id is None:
            # This is a new record, so insert it.
            await self._engine.insert(self)
        else:
            # This is an existing record, so update it.
            await self._engine.update(self)

    async def delete(self):
        """
        Deletes the current instance from the database.
        Delegates to the engine's delete method.
        """
        await self._engine.delete(self)
