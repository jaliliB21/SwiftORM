import importlib
from .core.models import _model_registry, Model


_engine = None


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
    # ... (rest of the function is the same)
    module_path, class_name = engine_path.rsplit('.', 1)
    engine_module = importlib.import_module(module_path)
    engine_class = getattr(engine_module, class_name)
    _engine = engine_class(db_config)

    Model._engine = _engine
    print(f"Engine '{class_name}' loaded and connected to models.")


async def connect():
    """Establishes the global database connection."""
    if not _engine:
        raise Exception("Engine is not set up. Call swiftorm.setup() first.")
    await _engine.connect()


async def disconnect():
    """Closes the global database connection."""
    if _engine:
        await _engine.disconnect()


async def create_all_tables():
    # ... (this function remains the same)
    if not _engine:
        raise Exception("Engine is not set up. Call swiftorm.setup() first.")

    
    for model_class in _model_registry:
        await _engine.create_table(model_class)