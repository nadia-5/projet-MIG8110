import importlib
import click

@click.command()
@click.option('--module',  type=click.Choice(['datalake', 'operations', 'datawarehouse']), required=True, help='Name of the process to run')
@click.option('--transformation_name', type=str, required=True, help='Name of the process to run')
def load_transformation(module: str, transformation_name: str):
    click.echo(f"Running transformation '{transformation_name}' from module '{module}'")
    try:
        module_path = getattr(importlib.import_module(f"proct_olis.{module}"), transformation_name)
        transformation_class = getattr(module_path, "Transformation")
        transformation_class().process()
    except ImportError:
        click.echo(f"Could not find and load transformation: {transformation_name} in module: {module}.")

def main():
    load_transformation(standalone_mode=False)