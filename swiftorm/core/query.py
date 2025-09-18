from . import exceptions


class QuerySet:
    """
    Manages and executes database queries for a model.
    """
    def __init__(self, model_class):
        self.model_class = model_class

    async def get(self, **kwargs):
        """
        Fetches exactly one record from the database.
        """
        # We fetch the engine from the model class dynamically,
        # ensuring we get the configured engine after setup() has run.
        engine = self.model_class._engine
        if not engine:
            raise exceptions.ORMError("Engine is not configured. Did you run swiftorm.setup()?")

        rows = await engine.select(self.model_class, **kwargs)

        if len(rows) == 0:
            raise exceptions.ObjectNotFound(f"{self.model_class.__name__} matching query does not exist.")
        
        if len(rows) > 1:
            raise exceptions.MultipleObjectsReturned(f"Query returned {len(rows)} objects, but expected 1.")
        
        instance = self.model_class(**rows[0])
        instance.id = rows[0].get('id') # Ensure PK is set
        return instance