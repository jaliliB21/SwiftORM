from async_driver.driver import Driver as PGDriver
from ..core.fields import IntegerField, TextField, BooleanField
from .base import BaseEngine
from ..core.models import Model
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

    # --- NEWLY IMPLEMENTED METHODS ---
    async def insert(self, model_instance):
        """
        Builds and executes an INSERT statement.
        """
        table_name = model_instance.__tablename__
        fields = model_instance._fields
        
        # Get columns and values from the instance
        columns = [f'"{name}"' for name in fields.keys() if getattr(model_instance, name, None) is not None]
        values = [getattr(model_instance, name) for name in fields.keys() if getattr(model_instance, name, None) is not None]
        
        # Build placeholders like $1, $2, $3
        placeholders = ', '.join([f'${i+1}' for i in range(len(values))])
        
        # Find the primary key field name
        pk_field_name = 'id' # Assume 'id' for now for simplicity
        
        sql = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({placeholders}) RETURNING "{pk_field_name}";'
        
        result = await self.driver.execute(sql, values)
        # Set the primary key on the instance after creation
        setattr(model_instance, pk_field_name, result[0][pk_field_name])

    async def update(self, model_instance):
        """
        Builds and executes an UPDATE statement.
        """
        table_name = model_instance.__tablename__
        fields = model_instance._fields
        pk_field_name = 'id' # Assume 'id' for now
        pk_value = getattr(model_instance, pk_field_name)

        update_fields = []
        values = []
        i = 1
        for name in fields.keys():
            if name != pk_field_name:
                update_fields.append(f'"{name}" = ${i}')
                values.append(getattr(model_instance, name))
                i += 1
        
        # Add the primary key value for the WHERE clause
        values.append(pk_value)
        
        sql = f'UPDATE "{table_name}" SET {", ".join(update_fields)} WHERE "{pk_field_name}" = ${i};'
        
        await self.driver.execute(sql, values)

    async def delete(self, model_instance):
        """
        Builds and executes a DELETE statement.
        """
        table_name = model_instance.__tablename__
        pk_field_name = 'id' # Assume 'id' for now
        pk_value = getattr(model_instance, pk_field_name)
        
        sql = f'DELETE FROM "{table_name}" WHERE "{pk_field_name}" = $1;'
        
        await self.driver.execute(sql, [pk_value])
