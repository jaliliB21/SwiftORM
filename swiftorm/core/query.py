from . import exceptions
import copy


class QuerySet:
    """
    Manages and executes database queries for a model.
    """
    def __init__(self, model_class):
        self.model_class = model_class
        # This will now store our WHERE conditions
        self._filters = {}

    def filter(self, **kwargs):
        """
        Adds a filter condition to the query. This is chainable.
        """
        # We create a clone of the current QuerySet to ensure
        # that chaining does not modify the original QuerySet.
        new_queryset = copy.deepcopy(self)
        new_queryset._filters.update(kwargs)
        return new_queryset

    async def all(self):
        """
        Executes the query and returns all matching records as a list.
        """
        engine = self.model_class._engine
        if not engine:
            raise exceptions.ORMError("Engine is not configured.")
        
        # Pass the stored filters to the engine's select method
        rows = await engine.select(self.model_class, **self._filters)
        
        # Convert raw data rows into model instances
        return [self.model_class(**row) for row in rows]


    async def get(self, **kwargs):
        """
        Fetches exactly one record from the database.
        """
        # We fetch the engine from the model class dynamically,
        # ensuring we get the configured engine after setup() has run.
        engine = self.model_class._engine
        if not engine:
            raise exceptions.ORMError("Engine is not configured.")

        rows = await engine.select(self.model_class, **kwargs)

        if len(rows) == 0:
            raise exceptions.ObjectNotFound(f"{self.model_class.__name__} matching query does not exist.")
        
        if len(rows) > 1:
            raise exceptions.MultipleObjectsReturned(f"Query returned {len(rows)} objects, but expected 1.")
        
        instance = self.model_class(**rows[0])
        instance.id = rows[0].get('id') # Ensure PK is set
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
        return instance