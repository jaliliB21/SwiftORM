import asyncio
import swiftorm
from user_app.models import User
from swiftorm.core import exceptions


async def main():
    swiftorm.setup('settings')
    await swiftorm.connect()
    await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS users;", [])
    await swiftorm.create_all_tables()

    try:
        # --- Test 1: Type Validation (should fail) ---
        print("\n--- 1. Testing Type Validation ---")
        try:
            # This should fail because username is not a string.
            await User.create(username=12345, email='badtype@example.com')
        except exceptions.ValidationError as e:
            print(f"SUCCESS: Correctly caught ValidationError for wrong type: {e}")

        # --- Test 2: Successful creation ---
        print("\n--- 2. Testing Successful Creation ---")
        user = await User.create(username='behzad', email='behzad@example.com')
        print(f"SUCCESS: Created user: {user}")


        # -- Test 3
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
        await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS users;", [])
        await swiftorm.disconnect()


if __name__ == "__main__":
    asyncio.run(main())