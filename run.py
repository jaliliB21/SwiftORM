import asyncio
import swiftorm

from user_app.models import User


async def main():

    swiftorm.setup('settings')
    
    try:
        await swiftorm.connect()
        await swiftorm.create_all_tables()
    
        print("\n--- Testing Create ---")
        new_user = await User.create(username='behzad')
        print(f"Created user: {new_user}")
        
        print("\n--- Testing Update ---")
        new_user.username = 'ali'
        await new_user.save()
        print(f"Updated user: {new_user}")
        
        print("\n--- Testing Delete ---")
        await new_user.delete()
        print(f"Deleted user with id: {new_user.id}")
        
    finally:
        print("Closing connection...")
        await swiftorm.disconnect()


if __name__ == "__main__":
    asyncio.run(main())