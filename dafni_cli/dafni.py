import click

from dafni_cli.commands.create import create
from dafni_cli.commands.delete import delete
from dafni_cli.commands.download import download
from dafni_cli.commands.get import get
from dafni_cli.commands.login import login, logout
from dafni_cli.commands.upload import upload
from dafni_cli.commands.validate import validate
from dafni_cli.version import DAFNI_CLI_VERSION


@click.group()
@click.version_option(version=DAFNI_CLI_VERSION)
def dafni():
    pass


dafni.add_command(login)
dafni.add_command(logout)
dafni.add_command(get)
dafni.add_command(delete)
dafni.add_command(upload)
dafni.add_command(download)
dafni.add_command(create)
dafni.add_command(validate)

if __name__ == "__main__":
    dafni()
