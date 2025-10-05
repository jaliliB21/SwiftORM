import pytest
from examples.blog.models import Author
from swiftorm.core import exceptions


@pytest.mark.asyncio
async def test_full_crud_cycle(db_session):
    """
    Tests a full Create, Read, Update, and Delete cycle on a simple model.
    This is an integration test that requires a live database.
    
    The `db_session` fixture is automatically used here to set up and
    tear down the database.
    """
    # 1. Create (C)
    print("Testing CREATE...")
    author = await Author.objects.create(name='Behzad')
    assert author.id is not None
    assert author.name == 'Behzad'
    
    # Keep the created ID for later steps
    author_id = author.id

    # 2. Read (R)
    print("Testing READ...")
    fetched_author = await Author.objects.get(id=author_id)
    assert fetched_author.id == author_id
    assert fetched_author.name == 'Behzad'
    
    # 3. Update (U)
    print("Testing UPDATE...")
    fetched_author.name = 'Ali'
    await fetched_author.save()
    
    # Verify the update by fetching again
    updated_author = await Author.objects.get(id=author_id)
    assert updated_author.name == 'Ali'
    
    # 4. Delete (D)
    print("Testing DELETE...")
    await updated_author.delete()
    
    # Verify the deletion by trying to fetch it again
    with pytest.raises(exceptions.ObjectNotFound):
        await Author.objects.get(id=author_id)