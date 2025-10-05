import pytest
import pytest_asyncio
import swiftorm


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    An async fixture that sets up the ORM, connects to the DB,
    creates tables for a clean slate, and then disconnects.
    """
    # 1. Setup the ORM using the example settings
    try:
        swiftorm.setup('examples.settings') 
    except ImportError:
        pytest.fail("Could not find 'examples.settings'. Make sure it exists in the 'examples' folder.")

    # 2. Connect to the database
    await swiftorm.connect()
    
    # 3. Clean up any old tables
    # We get the list of tables from the models that were discovered
    tables = [model.__tablename__ for model in swiftorm._model_registry]
    if tables:
        # First, we quote each table name.
        quoted_tables = [f'"{table}"' for table in tables]
        # Then we join the quoted names.
        await swiftorm.db.engine.driver.execute(f"DROP TABLE IF EXISTS {', '.join(quoted_tables)} CASCADE;", [])
    
    # 4. Create all tables
    await swiftorm.create_all_tables()
    
    # 5. Yield control to the test function
    # The test will run at this point.
    yield
    
    # 6. Teardown: Disconnect after the test is done
    await swiftorm.disconnect()