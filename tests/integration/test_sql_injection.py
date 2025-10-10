import pytest
import time
from examples.blog.models import Author, Product
from swiftorm.core import exceptions



@pytest.mark.asyncio
async def test_sql_injection_basic(db_session):
    """
    Tests basic SQL Injection: Malicious input should not bypass filters.
    """
    print("Testing basic SQL Injection...")
    
    # Create test data
    await Author.objects.create(name='Behzad')
    await Author.objects.create(name='Barad')
    
    # Test malicious input in filter (parameterized query should sanitize it)
    malicious_input = "' OR 1=1; --"
    filtered_malicious = await Author.objects.filter(name=malicious_input).all()
    assert isinstance(filtered_malicious, list)
    assert len(filtered_malicious) == 0  # Safe: No injection, empty result (not all records)
    
    print("Basic SQL Injection passed!")
    # No cleanup - fixture handles it


@pytest.mark.asyncio
async def test_sql_injection_union_select(db_session):
    """
    Tests UNION SELECT injection: Should not leak data from other tables.
    """
    print("Testing UNION SELECT injection...")
    
    # Create data in Author and Product (different tables)
    await Author.objects.create(name='Behzad')
    await Product.objects.create(sku='PROD1', name='Test Product', price='10.00')
    
    # Malicious UNION to steal from products
    malicious_union = "'; UNION SELECT name FROM products --"
    filtered = await Author.objects.filter(name=malicious_union).all()
    assert isinstance(filtered, list)
    assert len(filtered) == 0  # Safe: No leaked data from products
    
    print("UNION SELECT passed!")
    # No cleanup - fixture handles it


@pytest.mark.asyncio
async def test_sql_injection_blind(db_session):
    """
    Tests Blind SQL Injection: Should not cause abnormal behavior like delay.
    """
    print("Testing Blind SQL Injection...")
    
    # Create test data
    await Author.objects.create(name='Behzad')
    
    # Malicious blind input to cause delay if vulnerable (5 second WAITFOR)
    malicious_blind = "'; WAITFOR DELAY '00:00:05' --"
    start = time.time()
    filtered = await Author.objects.filter(name=malicious_blind).all()
    end = time.time()
    assert isinstance(filtered, list)
    assert len(filtered) == 0  # Safe: No delay or abnormal result
    assert end - start < 2  # No significant delay (under 2 seconds)
    
    print("Blind SQL Injection passed!")
    # No cleanup - fixture handles it


@pytest.mark.asyncio
async def test_sql_injection_numeric(db_session):
    """
    Tests numeric field injection: Should not return multiple or wrong objects.
    """
    print("Testing Numeric SQL Injection...")
    
    # Create test data
    await Author.objects.create(name='Behzad')
    
    # Malicious numeric input for id field
    malicious_numeric = "1 OR 1=1"  # Numeric injection for int fail
    with pytest.raises(exceptions.ValidationError):  # From field.validate
        await Author.objects.get(id=malicious_numeric)  # Fail with ValidationError
    
    print("Numeric SQL Injection passed!")
    # No cleanup - fixture handles it
