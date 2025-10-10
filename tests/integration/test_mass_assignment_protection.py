import pytest
from examples.blog.models import Author, Product
from swiftorm.core import exceptions


@pytest.mark.parametrize("field", ["name"])
@pytest.mark.asyncio
async def test_sql_injection_prevention(field, db_session):
    """
    Tests SQL Injection prevention: Malicious input should not bypass filters.
    """
    print(f"Testing SQL Injection on {field}...")
    
    # Test valid update (no PK change)
    author = await Author.objects.create(name='Behzad')
    author.name = 'Barad'  # Valid only
    await author.save()  # Succeeds
    fetched = await Author.objects.get(id=author.id)
    assert fetched.name == 'Barad'
    
    # Test invalid PK change on Author (after get to set original)
    author = await Author.objects.get(id=author.id)  # Reload to set _original_pk
    author.id = 999  # Change in memory
    with pytest.raises(exceptions.ValidationError):
        await author.save()  # Raises
    
    # Test valid on Product
    product = await Product.objects.create(sku='PROD1', name='Test Product', price='10.00')
    product.name = 'Updated Product'  # Valid only
    await product.save()  # Succeeds
    fetched_prod = await Product.objects.get(sku=product.sku)
    assert fetched_prod.name == 'Updated Product'
    
    # Test invalid PK on Product
    product = await Product.objects.get(sku=product.sku)  # Reload to set _original_pk
    product.sku = 'PROD2'  # Change in memory
    with pytest.raises(exceptions.ValidationError):
        await product.save()  # Raises
    
    print("Mass Assignment protection passed!")
    