from pathlib import Path
from typing import Optional

import click

import dafni_cli.api.workflows_api as workflows_api
from dafni_cli.api.exceptions import DAFNIError, ValidationError
from dafni_cli.api.session import DAFNISession
from dafni_cli.utils import optional_echo, print_json


def upload_workflow(
    session: DAFNISession,
    definition: Path,
    version_message: str,
    parent_id: Optional[str] = None,
    json: bool = False,
):
    """
    Uploads a workflow in JSON form to DAFNI.

    Args:
        session (DAFNISession): User session
        definition (Path): File path to the workflow definition file
        version_message (str): Version message to be included with this workflow version
        parent_id (str): ID of the parent workflow that this is an update of
        json (bool): Whether to print the raw json returned by the DAFNI API
    """

    # TODO: Validate workflow definition using workflows/validate?

    optional_echo("Uploading workflow", json)
    details = workflows_api.upload_workflow(
        session, definition, version_message, parent_id
    )

    if json:
        print_json(details)
    else:
        click.echo("\nUpload successful")
        click.echo(f"Version ID: {details['id']}")


def upload_parameter_set(session: DAFNISession, definition: Path, json: bool = False):
    """Uploads workflow parameter set to DAFNI

    Args:
        session (DAFNISession): User session
        definition (Path): File path to the parameter set definition file
        json (bool): Whether to print the raw json returned by the DAFNI API
    """

    optional_echo("Validating parameter set definition", json)
    try:
        workflows_api.validate_parameter_set_definition(session, definition)
    except ValidationError as err:
        click.echo(err)

        raise SystemExit(1) from err

    optional_echo("Uploading parameter set", json)

    try:
        details = workflows_api.upload_parameter_set(session, definition)
    except DAFNIError as err:
        click.echo(err)
        raise SystemExit(1) from err

    # Output details
    if json:
        print_json(details)
    else:
        click.echo("\nUpload successful")
        click.echo(f"Parameter set ID: {details['id']}")
