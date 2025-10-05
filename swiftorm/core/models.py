from abc import ABC, abstractmethod, ABCMeta
from .fields import Field, TextField, ForeignKey
from . import exceptions
from .. import db 


from .query import QuerySet

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
        foreign_keys = {} 
        for key, value in attrs.items():
            if isinstance(value, ForeignKey):
                foreign_keys[key] = value
            elif isinstance(value, Field):
                fields[key] = value
        
        setattr(new_class, '_fields', fields)
        setattr(new_class, '_foreign_keys', foreign_keys) # <-- Store it on the class
        
        # --- THIS IS THE NEW VALIDATION LOGIC ---
        # After gathering fields, we validate the primary key constraint.
        pk_count = sum(1 for f in fields.values() if f.primary_key)

        if pk_count == 0:
            raise TypeError(f"Model '{name}' must have one primary key field (primary_key=True).")
        if pk_count > 1:
            raise TypeError(f"Model '{name}' cannot have more than one primary key field.")
        # --- END OF NEW LOGIC ---
        

        # We now need to remove both types of fields from the class attributes
        for key in list(fields.keys()) + list(foreign_keys.keys()):
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
        It now expects foreign keys to be passed with an `_id` suffix.
        """
        all_fields = {**self._fields, **self._foreign_keys}

        self._is_new = True 
        
        # First, initialize all fields with their default value
        for name, field in all_fields.items():
            if isinstance(field, ForeignKey):
                setattr(self, f"{name}_id", field.default)
            else:
                setattr(self, name, field.default)

        # Then, overwrite with any values provided by the user
        for key, value in kwargs.items():
            # Check for regular fields OR fk fields with _id suffix
            if key in self._fields or (key.endswith('_id') and key[:-3] in self._foreign_keys):
                 setattr(self, key, value)
            # We don't check for the `author` object anymore, only `author_id`
            elif key in self._foreign_keys:
                 raise TypeError(f"'{key}' is a ForeignKey. To set it, pass '{key}_id' instead.")
            else:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __repr__(self):
        """
        A more robust representation that correctly displays the primary key and all fields.
        """
        all_fields = {**self._fields, **self._foreign_keys}
        attrs_list = []
        
        # Find and add the primary key first for clarity
        pk_name = self._get_pk_name()

        if pk_name:
             attrs_list.append(f"{pk_name}={getattr(self, pk_name, None)}")

        for key in sorted(all_fields.keys()):
            if key == pk_name: continue # Skip if it's the PK, we already added it
            
            if isinstance(all_fields[key], ForeignKey):
                attrs_list.append(f'{key}_id={getattr(self, f"{key}_id", None)}')
            else:
                attrs_list.append(f'{key}={getattr(self, key, None)}')
        return f"<{type(self).__name__}: {', '.join(attrs_list)}>"

    @classmethod
    def _get_pk_name(cls):
        """Finds the name of the primary key field for this model."""
        # Note: we use cls._fields instead of self._fields
        for name, field in cls._fields.items():
            if field.primary_key:
                return name
        return None

    def validate(self):
        """
        Runs validation checks for all fields, including ForeignKeys.
        """
        # We combine both dictionaries to check all fields.
        all_fields = {**self._fields, **self._foreign_keys}

        for name, field in all_fields.items():
            
            # For ForeignKeys, we check the `_id` attribute.
            if isinstance(field, ForeignKey):
                value = getattr(self, f"{name}_id", None)
            else:
                value = getattr(self, name, None)

            # Now we run the checks.
            if field.required and value is None:
                raise exceptions.ValidationError(f"Field '{name}' is required and cannot be null.")
            
            if value is not None:
                # We need to make sure we don't try to validate the related object itself,
                # just the value being saved.
                if not isinstance(field, ForeignKey):
                     field.validate(value)

    async def save(self):
        """
        Saves the current instance to the database.
        """
        
        self.validate()

        # We now use the `_is_new` flag to decide between INSERT and UPDATE
        if self._is_new:
            await db.engine.insert(self)
            # After the first insert, it's not new anymore
            self._is_new = False
        else:
            await db.engine.update(self)

    async def delete(self):
        """
        Deletes the current instance from the database.
        """
        pk_name = self._get_pk_name()
        pk_val = getattr(self, pk_name, None)
        
        if pk_val is None:
            raise exceptions.ORMError("Cannot delete an unsaved instance.")
        
        await db.engine.delete(self)
