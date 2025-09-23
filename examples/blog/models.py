from swiftorm.core.models import Model
from swiftorm.core.fields import IntegerField, TextField, ForeignKey


class Author(Model):
    __tablename__ = 'authors'
    id = IntegerField(primary_key=True)
    name = TextField(max_length=100, required=True)


class Post(Model):
    __tablename__ = 'posts'
    id = IntegerField(primary_key=True)
    title = TextField(max_length=200)
    
    # This defines the one-to-many relationship to the Author model.
    author = ForeignKey(to=Author, on_delete="CASCADE")
