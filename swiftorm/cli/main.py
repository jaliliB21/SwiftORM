import os
import click
import shutil
from pathlib import Path


# We find the path to our templates directory
# This is a robust way to locate files within our package
TEMPLATE_DIR = Path(__file__).parent / 'templates'


@click.group()
def cli():
    """A command-line tool for managing the SwiftORM framework."""
    pass


@cli.command()
def init():
    """
    Initializes a new SwiftORM project by creating settings.py and manage.py
    in the current directory.
    """
    click.echo("Initializing SwiftORM project...")

    # Define the files to be created
    files_to_create = {
        'manage.py.template': 'manage.py',
        'settings.py.template': 'settings.py',
    }

    for template_name, final_name in files_to_create.items():
        template_path = TEMPLATE_DIR / template_name
        destination_path = Path(os.getcwd()) / final_name

        if destination_path.exists():
            click.echo(f"'{final_name}' already exists. Skipping.")
        else:
            shutil.copy(str(template_path), str(destination_path))
            click.echo(f"Created '{final_name}'")

    click.echo("\nProject initialized successfully!")
    click.echo("Next steps:")
    click.echo("1. Configure your DATABASES in 'settings.py'.")
    click.echo("2. Run 'python manage.py startapp <app_name>' to create your first app.")