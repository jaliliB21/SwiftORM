import asyncio
import swiftorm
from user_app.models import User
from swiftorm.core import exceptions


async def main():
    # 1. Setup and create tables
    swiftorm.setup('settings')
    
    # We will manage connection manually for the test
    await swiftorm.connect()
    
    # Drop the table first to start with a clean slate for each run
    await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS users;", [])
    await swiftorm.create_all_tables()

    try:
        # --- Test 1: Successful creation ---
        print("\n--- 1. Testing Successful Creation ---")
        user1 = await User.create(username='behzad', email='behzad@example.com')
        print(f"SUCCESS: Created user: {user1}")

        # --- Test 2: UNIQUE constraint violation ---
        print("\n--- 2. Testing UNIQUE constraint ---")
        try:
            # This should fail because 'behzad' already exists.
            await User.create(username='behzad', email='another@example.com')
        except exceptions.IntegrityError as e:
            print(f"SUCCESS: Correctly caught IntegrityError for duplicate username.")
            # print(e) # Uncomment to see the full database error

        # --- Test 3: REQUIRED constraint violation ---
        print("\n--- 3. Testing REQUIRED constraint ---")
        try:
            # This should fail because email is required.
            await User.create(username='ali')
        except exceptions.ValidationError as e:
            print(f"SUCCESS: Correctly caught ValidationError for missing required field.")
            # print(e) # Uncomment to see the validation message

        # --- Test 4: MAX_LENGTH constraint violation ---
        print("\n--- 4. Testing MAX_LENGTH constraint ---")
        try:
            long_username = "a" * 100 # 100 characters is longer than max_length=50
            # This should fail because the username is too long.
            await User.create(username=long_username, email="long@example.com")
        except exceptions.ValidationError as e:
            print(f"SUCCESS: Correctly caught ValidationError for max_length.")
            # print(e) # Uncomment to see the validation message

    except exceptions.ORMError as e:
        print(f"An unexpected ORM error occurred: {e}")
    finally:
        # 5. Clean up and disconnect
        print("\n--- Cleaning up ---")
        await swiftorm._engine.driver.execute("DROP TABLE users;", [])
        await swiftorm.disconnect()


if __name__ == "__main__":
    asyncio.run(main())