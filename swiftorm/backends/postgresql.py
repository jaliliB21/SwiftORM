from async_driver.driver import Driver as PGDriver
from ..core.fields import IntegerField, TextField, BooleanField
from .base import BaseEngine


# A corrected and more robust mapping from our Field classes to PostgreSQL type strings.
FIELD_TYPE_MAP = {
    IntegerField: 'INTEGER',
    TextField: 'TEXT',
    BooleanField: 'BOOLEAN',
}


class PostgresEngine(BaseEngine):
    """
    The concrete implementation of the database engine for PostgreSQL.
    This class knows how to speak PostgreSQL's SQL dialect.
    """
    def __init__(self, db_config):
        super().__init__(db_config)
        # It uses the low-level driver we built in the first project.
        self.driver = PGDriver(db_config)

    async def connect(self):
        """Connects to the PostgreSQL database using our custom driver."""
        print("Connecting to PostgreSQL...")
        await self.driver.connect()
        print("Connection successful.")

    async def disconnect(self):
        """Disconnects from the PostgreSQL database."""
        print("Disconnecting from PostgreSQL...")
        await self.driver.close()
        print("Disconnection successful.")

    async def create_table(self, model_class):
        """
        Builds and executes a 'CREATE TABLE' SQL statement for a given model.
        """
        table_name = model_class.__tablename__
        
        sql_columns = []
        for name, field in model_class._fields.items():
            # Look up the base SQL type from our corrected map.
            column_type = FIELD_TYPE_MAP.get(type(field), 'TEXT')
            
            # Add PRIMARY KEY constraint if specified.
            # Use SERIAL for integer primary keys for auto-incrementing behavior.
            if field.primary_key:
                if isinstance(field, IntegerField):
                    column_type = 'SERIAL PRIMARY KEY'
                else:
                    column_type += ' PRIMARY KEY'
            
            sql_columns.append(f'"{name}" {column_type}')
                
        columns_sql = ", ".join(sql_columns)
        
        # The final CREATE TABLE query
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql});'
        
        print(f"Executing: {create_sql}")
        
        # Execute the query using our driver's secure parameter execution method
        await self.driver.execute(create_sql, [])
        print(f"Table '{table_name}' created or already exists.")