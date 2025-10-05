import importlib
from .core.models import _model_registry, Model
from . import db # Import the new state module


def setup(settings_module_path: str):
    global _engine
    
    settings = importlib.import_module(settings_module_path)
    db_config = settings.DATABASES['default']
    
    # Load models from all installed apps.
    if hasattr(settings, 'INSTALLED_APPS'):
        for app_name in settings.INSTALLED_APPS:
            try:
                # This import should trigger the metaclass for all models in the app.
                importlib.import_module(f"{app_name}.models")
            except ImportError:
                print(f"Warning: Could not import models for app '{app_name}'.")

    engine_path = db_config['engine']

    module_path, class_name = engine_path.rsplit('.', 1)
    engine_module = importlib.import_module(module_path)
    engine_class = getattr(engine_module, class_name)

    # Create the engine and store it in our central `db` module
    db.engine = engine_class(db_config)
    print(f"Engine '{class_name}' loaded.")
    print(db.engine)


async def connect():
    """Establishes the global database connection."""
    if not db.engine: raise Exception("Engine not set up.")
    await db.engine.connect()


async def disconnect():
    """Closes the global database connection."""
    if db.engine: await db.engine.disconnect()


async def create_all_tables():
    if not db.engine: raise Exception("Engine not set up.")

    # Connection management should be handled by the caller (e.g., CLI command or startup event)
    for model_class in _model_registry:
        await db.engine.create_table(model_class)