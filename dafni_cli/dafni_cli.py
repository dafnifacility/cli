import sys
import click
from dafni_cli.get import get
from dafni_cli.login import login


@click.group()
@click.version_option(version="0.0.1")
def dafni_cli():
    pass


dafni_cli.add_command(login)
dafni_cli.add_command(get)

if __name__ == "__main__":
    dafni_cli()