# This is where the user of our framework defines their database settings.
DATABASES = {
    'default': {
        "engine": "swiftorm.backends.postgresql.PostgresEngine",
        "user": "myuser",
        "password": "mypassword",
        "database": "mydb",
        "host": "localhost",
        "port": 5432
    }
}


INSTALLED_APPS = [
    'examples.blog',
]