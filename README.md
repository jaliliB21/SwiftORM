# SwiftORM

A modern, asynchronous ORM for Python, built from scratch using `asyncio` and inspired by the simplicity of the Active Record pattern.

> **Note:** This project is a portfolio piece designed to showcase advanced software architecture and protocol implementation. It is under active development. For production use, please consider battle-tested libraries like `asyncpg` and `SQLAlchemy`.

## Key Features

- **Asynchronous Core:** Built entirely on Python's `asyncio` for high-performance, non-blocking database operations.
- **Secure by Default:**
    - **Authentication:** Implements the modern **SCRAM-SHA-256** challenge-response mechanism.
    - **Querying:** Uses the **Extended Query Protocol** for all queries, providing automatic protection against SQL Injection.
- **Powerful Querying Engine:**
    - **Active Record Pattern:** An intuitive, object-oriented API (`user.save()`, `user.delete()`).
    - **Advanced Lookups:** Supports `.get()`, `.filter()`, `.all()`, `.first()`, and `.order_by()`.
    - **Chained Queries:** Conditions can be chained together for clean and readable queries (e.g., `Model.objects.filter(...).order_by(...)`).
- **Flexible Schema Definition:**
    - **Dynamic Primary Keys:** Does not assume the primary key is named `id`.
    - **Relationships:** Supports `ForeignKey` relationships with `ON DELETE` rules.
    - **Constraints:** Translates field options like `required=True`, `unique=True`, and `max_length` into proper SQL constraints (`NOT NULL`, `UNIQUE`, `VARCHAR`).
- **Developer-Friendly CLI:** Includes a command-line tool (`swiftorm-admin`) for initializing projects and creating apps, inspired by Django.

---

## Usage Example

The following example demonstrates the core features of `SwiftORM` in a simple, asynchronous script.

```python
import asyncio
import swiftorm
from examples.blog.models import Author, Post

async def main():
    # 1. Initialize the framework and manage the connection
    swiftorm.setup('examples.settings')
    await swiftorm.connect()
    
    # Ensure tables exist (starts with a clean slate)
    await swiftorm._engine.driver.execute("DROP TABLE IF EXISTS posts, authors CASCADE;", [])
    await swiftorm.create_all_tables()

    # --- Create ---
    print("--- 1. Creating objects ---")
    author = await Author.objects.create(name='Behzad')
    post = await Post.objects.create(title='My First Post', author_id=author.id)
    print(f"Created: {author}")
    print(f"Created: {post}")

    # --- Read (Get and Filter) ---
    print("\n--- 2. Reading objects ---")
    
    # Get a single object by its primary key
    fetched_author = await Author.objects.get(id=author.id)
    print(f"Fetched with .get(): {fetched_author}")

    # Filter for a list of objects
    all_posts = await Post.objects.filter(author_id=author.id).all()
    print(f"Fetched with .filter(): {all_posts}")

    # --- Update ---
    print("\n--- 3. Updating an object ---")
    post.title = "My Awesome Updated Title"
    await post.save()
    print(f"Updated: {post}")

    # --- Delete ---
    print("\n--- 4. Deleting an object ---")
    await post.delete()
    remaining_posts = await Post.objects.filter(author_id=author.id).all()
    print(f"Deleted: Number of remaining posts for author is {len(remaining_posts)}")

    # Clean up the final object
    await author.delete()

    # 5. Disconnect cleanly
    await swiftorm.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Integration with Web Frameworks (like FastAPI)

`SwiftORM` is designed to integrate cleanly with modern web frameworks. Here is the general workflow for using it with FastAPI:

1.  **Project Setup:** You start your FastAPI project. Then, inside your project directory, you run `swiftorm-admin init` to generate the `settings.py` and `manage.py` files.

2.  **Create Apps:** You use `python manage.py startapp <app_name>` to create modular apps for your models (e.g., an app for `users`, an app for `products`).

3.  **Define Models and Schemas:**
    -   In your app's `models.py`, you define your database tables using `SwiftORM`'s `Model` and `Field` classes.
    -   In a separate `schemas.py`, you define your Pydantic schemas for API validation and serialization. These two are kept separate to maintain a clean architecture.

4.  **Write API Endpoints:** In your FastAPI router files, you write your endpoints. These endpoints will take Pydantic schemas as input, use `SwiftORM`'s query methods (e.g., `await User.objects.create(...)`) to interact with the database, and return the results.

5.  **Manage Connection Lifecycle:** In your main FastAPI file (`main.py`), you use the `startup` and `shutdown` events to call `swiftorm.connect()` and `swiftorm.disconnect()`. This ensures a single, persistent database connection pool is managed for the life of the application.

This workflow demonstrates how SwiftORM can be cleanly integrated with modern web frameworks.

## Development Setup

To run this project locally, you'll need **Python 3.8+** and **Docker**.

1.  **Clone Both Repositories:**
    First, clone both the ORM and the low-level driver into the same parent directory.
    ```bash
    # Clone the ORM (this project)
    git clone https://github.com/jaliliB21/SwiftORM.git
    
    # Clone the driver project
    git clone https://github.com/jaliliB21/async-postgres-driver.git
    ```

2.  **Start the Database:**
    Navigate into the `async-postgres-driver` directory to use its `docker-compose.yml`.
    ```bash
    cd async-postgres-driver
    docker-compose up -d
    cd .. # Go back to the parent directory
    ```

3.  **Install Dependencies for SwiftORM:**
    Set up a virtual environment inside the `SwiftORM` project.
    ```bash
    cd SwiftORM
    python -m venv venv
    source venv/bin/activate
    
    # Install the low-level driver in editable mode
    # This command assumes the driver folder is one level up
    pip install -e ../async-postgres-driver
    
    # Install other dependencies for the ORM
    pip install -r requirements.txt
    ```

