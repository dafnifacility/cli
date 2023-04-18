import click

from dafni_cli.api.session import DAFNISession


@click.command(help="Login to DAFNI")
def login():
    """
    Log into the DAFNI CLI if needed after requesting the user's username
    and password. If there is already a cached session this will instead
    output the current logged in username and user_id.
    """

    if DAFNISession.has_session_file():
        # Output current stored session's username and user id
        session = DAFNISession()
        click.echo(f"Already logged in as {session.username}")
    else:
        # Creating a new session will request authentication anyway
        DAFNISession()


@click.command(help="Logout of DAFNI")
def logout():
    """
    Log out of the DAFNI CLI. Removes any cached session data.
    """

    if DAFNISession.has_session_file():
        session = DAFNISession()
        session.logout()

        click.echo("Logout complete")
    else:
        click.echo("Already logged out")
