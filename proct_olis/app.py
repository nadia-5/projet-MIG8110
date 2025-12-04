import importlib
import click

@click.command()
@click.option('--module',  type=click.Choice(['datalake', 'operations', 'datawarehouse']), required=True, help='Name of the process to run')
@click.option('--transformation_name', type=str, required=True, help='Name of the process to run')
@click.option('--extract_date', type=str, required=False, help='Date of Extraction')
def load_transformation(module: str, transformation_name: str, extract_date: str):
    print("Execution Date", extract_date)
    click.echo(f"Running transformation '{transformation_name}' from module '{module}'")
    try:
        module = importlib.import_module(f"proct_olis.{module}.{transformation_name}.model")

        print("######", module, "#####")
        transformation_class = getattr(module, "Transformation")
        instance = transformation_class(extract_date=extract_date)
        instance.process()
    except ImportError:
        click.echo(f"Could not find and load transformation: {transformation_name} in module: {module}.")

def main():
    load_transformation(standalone_mode=False)