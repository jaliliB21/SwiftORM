import importlib
from .core.models import _model_registry


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
    print(f"Engine '{class_name}' loaded successfully.")


async def create_all_tables():
    # ... (this function remains the same)
    if not _engine:
        raise Exception("Engine is not set up. Call swiftorm.setup() first.")
    await _engine.connect()
    try:
        for model_class in _model_registry:
            await _engine.create_table(model_class)
    finally:
        await _engine.disconnect()