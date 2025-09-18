# run.py
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
        print("\n--- Testing Create ---")
        user = await User.objects.create(username='behzad', email='behzad@example.com')
        
        print(f"Created user: {user}")
        
        # --- NEW TEST FOR .objects.get() ---
        print("\n--- Testing .objects.get() ---")
        
        # Test 1: Successful get
        fetched_user = await User.objects.get(id=user.id)
        print(f"SUCCESS: Fetched user by id: {fetched_user}")
        
        # Test 2: Object not found
        print("\n--- Testing .objects.get() with non-existent id ---")
        try:
            await User.objects.get(id=999)
        except exceptions.ObjectNotFound as e:
            print(f"SUCCESS: Correctly caught ObjectNotFound: {e}")
        
    except exceptions.ORMError as e:
        print(f"An ORM error occurred: {e}")
    finally:
        await swiftorm.disconnect()

if __name__ == "__main__":
    asyncio.run(main())