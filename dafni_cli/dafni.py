import click

from dafni_cli.commands.delete import delete
from dafni_cli.commands.download import download
from dafni_cli.commands.get import get
from dafni_cli.commands.login import login, logout
from dafni_cli.commands.upload import upload


@click.group()
@click.version_option(version="0.0.1")
def dafni():
    pass


dafni.add_command(login)
dafni.add_command(logout)
dafni.add_command(get)
dafni.add_command(delete)
dafni.add_command(upload)
dafni.add_command(download)

if __name__ == "__main__":
    dafni()
