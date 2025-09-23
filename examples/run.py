import asyncio
import swiftorm
# We import the models from our example app
from .blog.models import Author, Post


async def main():
    print("--- Setting up SwiftORM ---")
    # Note the path to the settings file
    swiftorm.setup('examples.settings')
    
    await swiftorm.connect()
    
    # Clean up previous tables for a fresh start
    print("\n--- Dropping old tables (if they exist) ---")
    await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS posts;", [])
    await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS authors;", [])
    
    # Create tables based on discovered models
    print("\n--- Creating new tables ---")
    await swiftorm.create_all_tables()
    
    print("\n--- Running example scenario ---")
    try:
        # 1. Create an Author
        author = await Author.objects.create(name='Behzad')
        print(f"Created Author: {author}")
        
        # 2. Create a Post and link it to the author using the ID
        post = await Post.objects.create(title='My First Post with SwiftORM', author_id=author.id)
        print(f"Created Post: {post}")
        
        # 3. Fetch the post and verify the relationship
        fetched_post = await Post.objects.get(id=post.id)
        print(f"Fetched post has author_id: {fetched_post.author_id}")
        assert fetched_post.author_id == author.id

        fetched_author_post = await Post.objects.filter(author_id=author.id).all()
        print(fetched_author_post)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\n--- Disconnecting ---")
        await swiftorm.disconnect()

if __name__ == "__main__":
    # To run this script, you must be in the project's ROOT directory
    # and use the command: python -m examples.run
    asyncio.run(main())