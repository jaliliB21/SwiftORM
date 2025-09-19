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
        # --- Setup: Create some initial data ---
        print("\n--- 1. Creating initial data ---")
        await User.objects.create(username='behzad', email='behzad@example.com', is_active=True)
        await User.objects.create(username='barad', email='barad@example.com', is_active=True)
        await User.objects.create(username='reza', email='reza@example.com', is_active=False)
        print("Initial data created successfully.")

        # --- Test 2: Using .filter() and .all() ---
        print("\n--- 2. Testing .filter().all() ---")
        active_users = await User.objects.filter(is_active=True).all()
        
        print(f"Found {len(active_users)} active users:")
        for user in active_users:
            print(f"  - {user}")
        
        assert len(active_users) == 2

        # --- Test 3: Chaining .filter() calls ---
        print("\n--- 3. Testing chained .filter() ---")
        behzad_active = await User.objects.filter(is_active=True).filter(username='behzad').all()
        
        print(f"Found {len(behzad_active)} active users named 'behzad'.")
        assert len(behzad_active) == 1
        assert behzad_active[0].username == 'behzad'
        
        # --- Test 4: Using .get() ---
        print("\n--- 4. Testing .get() ---")
        reza = await User.objects.get(username='reza')
        print(f"Fetched user with .get(): {reza}")
        assert reza.is_active is False
        
    except exceptions.ORMError as e:
        print(f"An ORM error occurred: {e}")
    finally:
        await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS users;", [])
        await swiftorm.disconnect()


if __name__ == "__main__":
    asyncio.run(main())