import pytest
from examples.blog.models import Author
from swiftorm.core import exceptions


@pytest.mark.parametrize("field", ["name"])
@pytest.mark.asyncio
async def test_query_methods(field, db_session):
    """
    Tests filter, order_by, and first methods (using builder chain).
    """
    print(f"Testing query methods on {field}...")
    
    # Create test data once for all methods
    await Author.objects.create(name='Barad')
    await Author.objects.create(name='Behzad')
    await Author.objects.create(name='Barad')  # For filter multiple
    
    # Test filter: Builder returns list after .all()
    filtered = await Author.objects.filter(name='Barad').all()
    assert isinstance(filtered, list)
    assert len(filtered) == 2
    assert all(a.name == 'Barad' for a in filtered)
    
    # Test order_by: Ascending and descending
    ordered_asc = await Author.objects.order_by('name').all()
    assert isinstance(ordered_asc, list)
    assert ordered_asc[0].name <= ordered_asc[1].name  # Barad first
    
    ordered_desc = await Author.objects.order_by('-name').all()
    assert ordered_desc[0].name >= ordered_desc[1].name  # Behzad first
    
    # Test first: Builder returns first object after .first()
    first_author = await Author.objects.first()
    assert first_author is not None
    assert isinstance(first_author, Author)
    assert first_author.name in ['Barad', 'Behzad']  # One of the created
    
    print("Query methods passed!")
    
    # Clean up once
    authors = await Author.objects.all()
    for author in authors:
        await author.delete()


@pytest.mark.parametrize("field", ["name"])
@pytest.mark.asyncio
async def test_get_exceptions(field, db_session):
    """
    Tests get method with ObjectNotFound and MultipleObjectsReturned exceptions.
    """
    print(f"Testing get exceptions on {field}...")
    
    # Create test data
    await Author.objects.create(name='Behzad')
    await Author.objects.create(name='Barad')
    await Author.objects.create(name='Barad')  # For multiple
    
    # Test get single object
    single_author = await Author.objects.get(name='Behzad')
    assert single_author.name == 'Behzad'
    
    # Test ObjectNotFound
    with pytest.raises(exceptions.ObjectNotFound):
        await Author.objects.get(id=999)  # Non-existent ID
    
    # Test MultipleObjectsReturned
    with pytest.raises(exceptions.MultipleObjectsReturned):
        await Author.objects.get(name='Barad')  # Multiple matches
    
    print("Get exceptions passed!")
    
    # Clean up
    authors = await Author.objects.all()
    for author in authors:
        await author.delete()