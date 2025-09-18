from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """
    The abstract base class for all database engines.
    It defines the contract that every engine must adhere to.
    """
    def __init__(self, db_config):
        self.db_config = db_config

    @abstractmethod
    async def connect(self):
        """Establishes a connection to the database."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self):
        """Closes the connection to the database."""
        raise NotImplementedError

    @abstractmethod
    async def create_table(self, model_class):
        """Creates a database table based on a model class."""
        raise NotImplementedError
    
     # --- ABSTRACT METHODS FOR CRUD ---
    @abstractmethod
    async def insert(self, model_instance):
        """Inserts a new record into the database."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, model_instance):
        """Updates an existing record in the database."""
        raise NotImplementedError
        
    @abstractmethod
    async def delete(self, model_instance):
        """Deletes a record from the database."""
        raise NotImplementedError

    @abstractmethod
    async def select(self, model_class, **kwargs):
        """Selects records from the database."""
        raise NotImplementedError
