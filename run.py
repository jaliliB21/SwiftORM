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
        # --- 1. Create initial data ---
        print("\n--- 1. Creating initial data ---")
        await User.objects.create(username='behzad', email='behzad@example.com', is_active=True)
        await User.objects.create(username='ali', email='ali@example.com', is_active=True)
        await User.objects.create(username='reza', email='reza@example.com', is_active=False)
        print("Initial data created successfully.")

        # --- 2. Test .order_by() and .first() ---
        print("\n--- 2. Testing .order_by() and .first() ---")
        # Get the first active user, ordered by username descending
        first_active_user = await User.objects.filter(is_active=True).order_by('-username').first()
        
        print(f"SUCCESS: The first active user (ordered by name DESC) is: {first_active_user}")
        # 'behzad' comes after 'ali' alphabetically, so it should be first in DESC order.
        assert first_active_user.username == 'behzad'
        
        # --- 3. Test .all() with ordering ---
        print("\n--- 3. Testing .all() with ordering ---")
        all_active_users = await User.objects.filter(is_active=True).order_by('username').all()
        print("SUCCESS: Active users ordered by name ASC:")
        for user in all_active_users:
            print(f"  - {user}")
        assert all_active_users[0].username == 'ali'
        assert all_active_users[1].username == 'behzad'

    except exceptions.ORMError as e:
        print(f"An ORM error occurred: {e}")
    finally:
        await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS users;", [])
        await swiftorm.disconnect()


if __name__ == "__main__":
    asyncio.run(main())