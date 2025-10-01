import pytest
from swiftorm.core.models import Model
from swiftorm.core.fields import IntegerField, TextField, ForeignKey


# --- Helper Models for Testing ---
# We define these at the top level of the module so they are available to all tests.
class User(Model):
    id = IntegerField(primary_key=True)
    username = TextField(required=True)


class Post(Model):
    id = IntegerField(primary_key=True)
    title = TextField()
    author = ForeignKey(to=User, on_delete="CASCADE")


def test_model_with_multiple_pks_raises_error():
    """
    Tests that defining a model with more than one primary_key=True
    raises a TypeError at class creation time.
    """
    with pytest.raises(TypeError, match="cannot have more than one primary key"):
        # This class definition is intentionally wrong.
        class Product(Model):
            id = IntegerField(primary_key=True)
            product_code = TextField(primary_key=True)
            name = TextField()


def test_model_with_no_pk_raises_error():
    """
    Tests that defining a model with no primary key raises a TypeError.
    """
    with pytest.raises(TypeError, match="must have one primary key field"):
        # This class is also intentionally wrong.
        class Order(Model):
            order_date = TextField()
            total_amount = IntegerField()


def test_model_with_one_pk_is_valid():
    """
    Tests that a correctly defined model (with one PK) can be
    created without raising any errors.
    """
    try:
        # This class definition is correct and should NOT raise an error.
        class User(Model):
            __tablename__ = 'users_test' # Use a different name to avoid conflicts
            id = IntegerField(primary_key=True)
            username = TextField()
    except TypeError:
        pytest.fail("A correctly defined model should not raise a TypeError.")


def test_get_pk_name_method():
    """
    Tests that the _get_pk_name classmethod correctly identifies
    the name of the primary key field.
    """
    class CorrectProduct(Model):
        product_sku = TextField(primary_key=True)
        name = TextField()

    class CorrectUser(Model):
        id = IntegerField(primary_key=True)
        name = TextField()

    assert CorrectProduct._get_pk_name() == 'product_sku'
    assert CorrectUser._get_pk_name() == 'id'


def test_model_initialization():
    """
    Tests that a model instance is initialized correctly.
    - Default values should be set.
    - Passed values should override defaults.
    """
    # 1. Test initialization with provided values
    user = User(id=1, username='behzad')
    assert user.id == 1
    assert user.username == 'behzad'

    # 2. Test initialization with foreign key ID
    post = Post(id=1, title='My Post', author_id=1)
    assert post.id == 1
    assert post.title == 'My Post'
    assert post.author_id == 1


def test_model_initialization_with_extra_field_raises_error():
    """
    Tests that creating an instance with an undefined field raises AttributeError.
    This prevents Mass Assignment vulnerabilities.
    """
    with pytest.raises(AttributeError, match="'User' object has no attribute 'is_admin'"):
        # This should fail because `is_admin` is not a defined field on the User model.
        User(id=1, username='test', is_admin=True)


def test_model_repr():
    """
    Tests the __repr__ method for a clean string representation.
    """
    user = User(id=1, username='behzad')
    post = Post(id=10, title='A Title', author_id=1)
    
    # Check the string representation
    assert repr(user) == "<User: id=1, username=behzad>"
    # Note: `author_id` is shown because of our improved __repr__
    assert repr(post) == "<Post: id=10, author_id=1, title=A Title>"
