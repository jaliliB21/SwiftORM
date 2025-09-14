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
    
    # We will add more abstract methods here later for insert, select, etc.

