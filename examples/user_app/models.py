from swiftorm.core.models import Model
from swiftorm.core.fields import IntegerField, TextField, BooleanField


class User(Model):
    __tablename__ = 'users'
    
    # id will be SERIAL PRIMARY KEY
    id = IntegerField(primary_key=True)
    
    # username will be VARCHAR(50) NOT NULL UNIQUE
    username = TextField(max_length=50, required=True, unique=True)
    
    # email will be TEXT NOT NULL UNIQUE
    email = TextField(required=True, unique=True)
    
    # is_active will be BOOLEAN
    is_active = BooleanField(default=True)