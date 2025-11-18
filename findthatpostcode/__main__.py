import click

from findthatpostcode.commands import check_cli, import_cli
from findthatpostcode.db import init_db_command


@click.group()
def main_cli():
    pass


main_cli.add_command(import_cli)
main_cli.add_command(check_cli)
main_cli.add_command(init_db_command)

if __name__ == "__main__":
    main_cli()
