import click

from findthatpostcode.commands import check_cli, import_cli
from findthatpostcode.commands.utils import json_to_python
from findthatpostcode.db import init_db_command


@click.group()
def main_cli():
    pass


main_cli.add_command(import_cli)
main_cli.add_command(check_cli)
main_cli.add_command(init_db_command)


@main_cli.command("areatypes-to-python")
@click.argument(
    "file_path", type=click.Path(exists=True), default="findthatpostcode/areatypes.py"
)
def json_to_python_command(file_path: str) -> None:
    """Convert a JSON file to a Python file containing a dictionary."""
    json_to_python(file_path)


if __name__ == "__main__":
    main_cli()
