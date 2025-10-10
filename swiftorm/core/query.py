from . import exceptions
from .. import db
import copy


from async_driver.exceptions import QueryError


class QuerySet:
    """
    Manages and executes database queries for a model.
    """
    def __init__(self, model_class):
        self.model_class = model_class
        # This will now store our WHERE conditions
        self._filters = {}
        # This new list will store our ORDER BY conditions
        self._ordering = []

    def validate_filters(self):
        """
        Validates all filters in self._filters using the model's field validators.
        Raises ValidationError if any value is invalid for its field type.
        """
        for key, value in self._filters.items():
            field = self.model_class._fields.get(key)
            if field:
                field.validate(value)  # Raise ValidationError if invalid (e.g., string for int)

    def filter(self, **kwargs):
        """
        Adds a filter condition to the query. This is chainable.
        """
        # We create a clone of the current QuerySet to ensure
        # that chaining does not modify the original QuerySet.
        new_queryset = copy.deepcopy(self)
        new_queryset._filters.update(kwargs)
        return new_queryset

    def order_by(self, *args):
        """
        Adds an ordering condition to the query. This is chainable.
        e.g., .order_by('username', '-id')
        """
        new_queryset = copy.deepcopy(self)
        new_queryset._ordering.extend(args)
        return new_queryset

    async def all(self):
        """
        Executes the query and returns all matching records as a list.
        """
        engine = db.engine
        if not engine:
            raise exceptions.ORMError("Engine is not configured.")

        self.validate_filters() # Validate self._filters
        try:
            # Pass the stored filters to the engine's select method
            rows = await engine.select(
                self.model_class,
                filters=self._filters,
                ordering=self._ordering  # <-- Pass ordering to the engine
            )
        except QueryError as e:
            error_msg = str(e).lower()
            if "invalid input syntax" in error_msg:
                raise exceptions.ValidationError(f"Invalid input for query: {str(e)}")
            raise  # Re-raise other QueryErrors
        
        # Convert raw data rows into model instances
        results = []
        for row in rows:
            instance = self.model_class(**row)
            instance._is_new = False # <-- THE FIX
            results.append(instance)
        return results

    async def first(self):
        """
        Executes the query and returns the first matching record, or None.
        """
        engine = db.engine
        if not engine:
            raise exceptions.ORMError("Engine is not configured.")

        
        self.validate_filters() # Validate self._filters
        try:
            # Limit the query to 1 result for efficiency
            rows = await engine.select(
                self.model_class,
                filters=self._filters,
                ordering=self._ordering,
                limit=1
            )
        except QueryError as e:
            error_msg = str(e).lower()
            if "invalid input syntax" in error_msg:
                raise exceptions.ValidationError(f"Invalid input for query: {str(e)}")
            raise  # Re-raise other QueryErrors

        if not rows:
            return None
        
        # We need to correctly initialize the instance from the row data
        instance = self.model_class(**rows[0])
        instance._is_new = False

        return instance

    async def get(self, **kwargs):
        """
        Fetches exactly one record from the database.
        """
        # We fetch the engine from the model class dynamically,
        # ensuring we get the configured engine after setup() has run.
        engine = db.engine
        if not engine:
            raise exceptions.ORMError("Engine is not configured.")


        self.validate_filters() # Validate kwargs (set self._filters if needed)
        try:
            rows = await engine.select(self.model_class, filters=kwargs)
        except QueryError as e:
            error_msg = str(e).lower()
            if "invalid input syntax" in error_msg:
                raise exceptions.ValidationError(f"Invalid input for query: {str(e)}")
            raise  # Re-raise other QueryErrors

        if len(rows) == 0:
            raise exceptions.ObjectNotFound(f"{self.model_class.__name__} matching query does not exist.")
        
        if len(rows) > 1:
            raise exceptions.MultipleObjectsReturned(f"Query returned {len(rows)} objects, but expected 1.")
        
        instance = self.model_class(**rows[0])
        instance._is_new = False
        instance._set_original_pk()  # Set original PK after load
        return instance

    async def create(self, **kwargs):
        """
        Creates a new instance, saves it, and returns it.
        This is the main factory method.
        """
        # Create an instance in memory
        instance = self.model_class(**kwargs)
        # Use the instance's own save method to persist it
        await instance.save()
        instance._set_original_pk()  # Set original PK after load
        return instance
