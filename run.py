import asyncio
import swiftorm


async def main():
    # Setup the ORM with the path to our settings file.
    swiftorm.setup('settings')
    
    # Create all tables based on the models discovered from INSTALLED_APPS.
    await swiftorm.create_all_tables()

if __name__ == "__main__":
    asyncio.run(main())