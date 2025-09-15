from swiftorm.core.models import Model
from swiftorm.core.fields import IntegerField, TextField


class User(Model):
    """A test model for our application."""
    __tablename__ = 'users'
    id = IntegerField(primary_key=True)
    username = TextField()