import pytest
from examples.blog.models import Author, Product
from swiftorm.core import exceptions


@pytest.mark.asyncio
async def test_required_constraints(db_session):
    """
    Tests REQUIRED constraints (NOT NULL) for fields with required=True.
    """

    print("Testing REQUIRED constraints...") 

    # Test REQUIRED: Author name is required (required=True)
    with pytest.raises(exceptions.ValidationError):
        await Author.objects.create(name=None)
    
    # Test REQUIRED: Product name is required
    with pytest.raises(exceptions.ValidationError):
        await Product.objects.create(sku='PROD1', name=None, price='10.00')
    
    # Test REQUIRED: Product price is required
    with pytest.raises(exceptions.ValidationError):
        await Product.objects.create(sku='PROD1', name='Product One', price=None)
    
    print("REQUIRED constraints passed!")
    
    # No cleanup needed as creations failed


@pytest.mark.asyncio
async def test_unique_constraints(db_session):
    """
    Tests UNIQUE constraints at database level (e.g., primary_key fields).
    """
    print("Testing UNIQUE constraints...")
    
    # Create a valid Product for UNIQUE test (sku is primary_key=True, so UNIQUE)
    product1 = await Product.objects.create(sku='PROD1', name='First Product', price='10.00')
    assert product1.sku == 'PROD1'
    
    # Test UNIQUE violation: Try duplicate sku
    with pytest.raises(exceptions.IntegrityError):  # DB-level unique violation
        await Product.objects.create(sku='PROD1', name='Duplicate Product', price='20.00')
    
    # Clean up
    await product1.delete()
    
    print("UNIQUE constraints passed!")