import click
from dafni_cli.get import get
from dafni_cli.login import login, logout
from dafni_cli.delete import delete


@click.group()
@click.version_option(version="0.0.1")
def dafni():
    pass


dafni.add_command(login)
dafni.add_command(logout)
dafni.add_command(get)
dafni.add_command(delete)

if __name__ == "__main__":
    dafni()
