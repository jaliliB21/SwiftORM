from async_driver.driver import Driver as PGDriver
from async_driver.exceptions import QueryError

from ..core.fields import IntegerField, TextField, BooleanField, ForeignKey
from .base import BaseEngine
from ..core.models import Model
from .base import BaseEngine
from ..core import exceptions

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

    async def create_table(self, model_class: Model):
        """
        Builds and executes a 'CREATE TABLE' SQL statement for a given model,
        now with support for ForeignKey constraints.
        """
        table_name = model_class.__tablename__
        
        sql_columns = []
        # We will collect table-level constraints like foreign keys separately.
        table_constraints = []
        all_fields = {**model_class._fields, **model_class._foreign_keys}

        for name, field in all_fields.items():
            
            # LOGIC FOR ForeignKey
            if isinstance(field, ForeignKey):
                # The actual column name will be `field_name_id`
                col_name = f'"{name}_id"'
                # Foreign key columns are typically integers
                column_type_str = 'INTEGER'
                
                related_table = field.related_model.__tablename__
                
                # Dynamic ID Field
                related_field = field.related_model._get_pk_name()
                
                # Build the FOREIGN KEY constraint string
                fk_constraint = (
                    f'CONSTRAINT fk_{table_name}_{name}_to_{related_table} '
                    f'FOREIGN KEY ({col_name}) REFERENCES "{related_table}" ("{related_field}") '
                    f'ON DELETE {field.on_delete.upper()}'
                )
                table_constraints.append(fk_constraint)
                
                # Create the column definition for the foreign key
                # It can also have other constraints like NOT NULL
                constraints = []
                if field.required:
                    constraints.append('NOT NULL')
                
                full_column_def = f'{col_name} {column_type_str} {" ".join(constraints)}'
                sql_columns.append(full_column_def.strip())

            # LOGIC FOR REGULAR FIELDS
            else:
                # Start with the base column type
                column_type_str = FIELD_TYPE_MAP.get(type(field), 'TEXT')
                
                # Special handling for TextField with max_length
                if isinstance(field, TextField) and field.max_length is not None:
                    column_type_str = f"VARCHAR({field.max_length})"

                constraints = []
                
                # Handle PRIMARY KEY (and SERIAL for integers)
                if field.primary_key:
                    if isinstance(field, IntegerField):
                        column_type_str = 'SERIAL'
                    constraints.append('PRIMARY KEY')
                
                # Handle REQUIRED (NOT NULL)
                if field.required:
                    constraints.append('NOT NULL')
                
                # Handle UNIQUE
                if field.unique:
                    constraints.append('UNIQUE')
                    
                # Assemble the final column definition string
                full_column_def = f'"{name}" {column_type_str} {" ".join(constraints)}'
                sql_columns.append(full_column_def.strip())
        
        # Add the table-level constraints at the end
        if table_constraints:
            sql_columns.extend(table_constraints)
            
        columns_sql = ", ".join(sql_columns)
        
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql});'
        
        print(f"Executing: {create_sql}")
        
        await self.driver.execute(create_sql, [])
        print(f"Table '{table_name}' created or already exists.")
    
    async def insert(self, model_instance):
        """
        Builds and executes an INSERT statement.
        """
        table_name = model_instance.__tablename__
        
        columns = []
        values = []
        all_fields = {**model_instance._fields, **model_instance._foreign_keys}

        # Dynamically find the primary key name
        pk_field_name = model_instance._get_pk_name()

        # This new, smarter loop handles all cases correctly.
        for name, field in all_fields.items():
            value = None
            col_name = name
            
            if isinstance(field, ForeignKey):
                col_name = f"{name}_id"
                value = getattr(model_instance, col_name, None)
            else:
                value = getattr(model_instance, name, None)
            
            # THE KEY LOGIC: We skip the primary key ONLY if it's an IntegerField
            # (which we assume is SERIAL) AND its value is None.
            # In all other cases (like a TextField PK), we include it.
            if field.primary_key and isinstance(field, IntegerField) and value is None:
                continue

            columns.append(f'"{col_name}"')
            values.append(value)
       
        # Build placeholders like $1, $2, $3
        placeholders = ', '.join([f'${i+1}' for i in range(len(values))])
                
        sql = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({placeholders})'

        # Only use RETURNING if the PK is an auto-generating integer.
        if pk_field_name and isinstance(model_instance._fields.get(pk_field_name), IntegerField):
            sql += f' RETURNING "{pk_field_name}";'
        else:
            sql += ';'

        try:
            result = await self.driver.execute(sql, values)
            
            # Only try to set the PK if the database returned a result.
            if pk_field_name and result and pk_field_name in result[0]:
                setattr(model_instance, pk_field_name, result[0][pk_field_name])
                
        except QueryError as e:
            # Check if the database error is about a unique constraint violation
            if 'unique constraint' in str(e).lower():
                raise exceptions.IntegrityError(f"A record with this value already exists. Details: {e}")
            else:
                # Re-raise other query errors
                raise e

    async def update(self, model_instance):
        """
        Builds and executes an UPDATE statement.
        """
        table_name = model_instance.__tablename__

        pk_field_name = model_instance._get_pk_name()
        pk_value = getattr(model_instance, pk_field_name)

        update_fields = []
        values = []
        i = 1
        
        # Combine all fields for updating
        all_fields = {**model_instance._fields, **model_instance._foreign_keys}

        for name, field in all_fields.items():
            if not field.primary_key:
                # Handle foreign keys by updating the `_id` column
                if isinstance(field, ForeignKey):
                    col_name = f"{name}_id"
                    update_fields.append(f'"{col_name}" = ${i}')
                    values.append(getattr(model_instance, col_name))
                # Handle regular fields
                else:
                    col_name = name
                    update_fields.append(f'"{col_name}" = ${i}')
                    values.append(getattr(model_instance, col_name))
                i += 1

        if not update_fields:
            return

        # Add the primary key value for the WHERE clause
        values.append(pk_value)
        
        sql = f'UPDATE "{table_name}" SET {", ".join(update_fields)} WHERE "{pk_field_name}" = ${i};'
        
        try:
            await self.driver.execute(sql, values)
        except QueryError as e:
            # Check if the database error is about a unique constraint violation
            if 'unique constraint' in str(e).lower():
                raise exceptions.IntegrityError(f"A record with this value already exists. Details: {e}")
            else:
                # Re-raise other query errors
                raise e

    async def delete(self, model_instance):
        """
        Builds and executes a DELETE statement.
        """
        table_name = model_instance.__tablename__
        pk_field_name = model_instance._get_pk_name()
        pk_value = getattr(model_instance, pk_field_name)
        
        sql = f'DELETE FROM "{table_name}" WHERE "{pk_field_name}" = $1;'
        
        await self.driver.execute(sql, [pk_value])

    async def select(self, model_class, filters={}, ordering=[], limit=None):
        """
        Builds and executes a SELECT ... WHERE ... statement.
        """
        table_name = model_class.__tablename__
        
        # The loop now correctly iterates over the `filters` dictionary
        # instead of the non-existent `kwargs`.
        where_clauses = []
        values = []
        i = 1
        for key, value in filters.items():
            where_clauses.append(f'"{key}" = ${i}')
            values.append(value)
            i += 1
        
        # Join all filter conditions together with 'AND'.
        where_sql = " AND ".join(where_clauses)
        
        sql = f'SELECT * FROM "{table_name}"'

        if where_sql:
            sql += f" WHERE {where_sql}"
        
        # --- LOGIC FOR ORDER BY ---
        if ordering:
            order_clauses = []
            for field_name in ordering:
                if field_name.startswith('-'):
                    # Handle descending order
                    order_clauses.append(f'"{field_name[1:]}" DESC')
                else:
                    # Handle ascending order
                    order_clauses.append(f'"{field_name}" ASC')
            sql += f" ORDER BY {', '.join(order_clauses)}"
        # --- END ---

        # --- LOGIC FOR LIMIT ---
        if limit is not None:
            sql += f" LIMIT {limit}"
        # --- END ---

        sql += ";"

        # Use the driver to execute the query and return the results
        return await self.driver.execute(sql, values)
