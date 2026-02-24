import click

from findthatpostcode.commands import check_cli, import_cli
from findthatpostcode.commands.utils import json_to_python
from findthatpostcode.crud.auth import create_super_user
from findthatpostcode.db import get_db, init_db_command
from findthatpostcode.security import password_context


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


@main_cli.command("add-super-user")
@click.argument("email", type=str)
def add_super_user_command(email: str) -> None:
    """Add a super user to the database."""
    print("Creating super user...")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    for db in get_db():
        user = create_super_user(password_context, db, email, password)
        click.echo(f"Super user created: {user.email}")


if __name__ == "__main__":
    main_cli()
