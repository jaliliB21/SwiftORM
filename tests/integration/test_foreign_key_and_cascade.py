import pytest
from examples.blog.models import Author, Post
from swiftorm.core import exceptions


@pytest.mark.parametrize("relation_type", ["one_to_many"])
@pytest.mark.asyncio
async def test_foreign_key_relationship(relation_type, db_session):
    """
    Tests ForeignKey creation and relationship access using author_id.
    """
    print(f"Testing {relation_type} relationship...")
    
    # Create an Author
    author = await Author.objects.create(name='Behzad')
    assert author.id is not None
    
    # Create Posts linked to the Author's ID
    post1 = await Post.objects.create(title='First Post', author_id=author.id)
    post2 = await Post.objects.create(title='Second Post', author_id=author.id)
    assert post1.id is not None
    assert post2.id is not None
    assert post1.author_id == author.id
    assert post2.author_id == author.id
    
    # Verify relationship by fetching Post and checking author_id
    fetched_post1 = await Post.objects.get(id=post1.id)
    assert fetched_post1.author_id == author.id
    
    # Fetch related Author using author_id
    fetched_author = await Author.objects.get(id=fetched_post1.author_id)
    assert fetched_author.name == 'Behzad'
    
    print("ForeignKey relationship passed!")


@pytest.mark.parametrize("relation_type", ["one_to_many"])
@pytest.mark.asyncio
async def test_on_delete_cascade(relation_type, db_session):
    """
    Tests ON DELETE CASCADE behavior for ForeignKey.
    """
    print(f"Testing {relation_type} ON DELETE CASCADE...")
    
    # Create an Author and linked Posts
    author = await Author.objects.create(name='Behzad')
    post1 = await Post.objects.create(title='First Post', author_id=author.id)
    post2 = await Post.objects.create(title='Second Post', author_id=author.id)
    
    # Store IDs for verification
    author_id = author.id
    post1_id = post1.id
    post2_id = post2.id
    
    # Delete Author and check CASCADE
    await author.delete()
    
    with pytest.raises(exceptions.ObjectNotFound):
        await Author.objects.get(id=author_id)
    
    with pytest.raises(exceptions.ObjectNotFound):
        await Post.objects.get(id=post1_id)
    
    with pytest.raises(exceptions.ObjectNotFound):
        await Post.objects.get(id=post2_id)
    
    print("ON DELETE CASCADE passed!")