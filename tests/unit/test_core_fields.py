import pytest
from swiftorm.core.fields import Field, IntegerField, TextField, BooleanField
from swiftorm.core import exceptions


def test_integer_field_validation():
    """
    Tests that IntegerField only accepts integers.
    """
    field = IntegerField()
    
    # This should work without errors
    field.validate(123)
    
    # This should raise a ValidationError
    with pytest.raises(exceptions.ValidationError, match="must be an integer"):
        field.validate("not a number")
        
    with pytest.raises(exceptions.ValidationError, match="must be an integer"):
        field.validate(12.34)


def test_text_field_validation():
    """
    Tests that TextField only accepts strings and respects max_length.
    """
    # Test 1: Basic string validation
    field_no_limit = TextField()
    field_no_limit.validate("this is a string")

    with pytest.raises(exceptions.ValidationError, match="must be a string"):
        field_no_limit.validate(123)

    # Test 2: max_length validation
    field_with_limit = TextField(max_length=10)
    field_with_limit.validate("short") # Should pass

    with pytest.raises(exceptions.ValidationError, match="exceeds max length"):
        field_with_limit.validate("this string is definitely too long")


def test_boolean_field_validation():
    """
    Tests that BooleanField only accepts booleans.
    """
    field = BooleanField()
    
    field.validate(True)
    field.validate(False)
    
    with pytest.raises(exceptions.ValidationError, match="must be a boolean"):
        field.validate("not a boolean")

    with pytest.raises(exceptions.ValidationError, match="must be a boolean"):
        field.validate(0)