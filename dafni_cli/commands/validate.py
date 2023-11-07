import json as json_lib
from pathlib import Path

import click
from click import Context

from dafni_cli.api.datasets_api import validate_metadata
from dafni_cli.api.exceptions import ValidationError
from dafni_cli.api.session import DAFNISession
from dafni_cli.commands.options import confirmation_skip_option
from dafni_cli.utils import argument_confirmation


###############################################################################
# COMMAND: Validation check an entity for DAFNI
###############################################################################
@click.group(help="Validation check an entity for DAFNI")
@click.pass_context
def validate(ctx: Context):
    """Validation check for entities (models, datasets, workflows, groups) for DAFNI.

    Args:
        ctx (Context): Context containing the user session.
        yes (bool): Used to skip confirmations before they are displayed
    """
    ctx.ensure_object(dict)
    ctx.obj["session"] = DAFNISession()


###############################################################################
# COMMAND: Validation check for metadata for DAFNI
###############################################################################
@validate.command(help="Validation check a dataset metadata for DAFNI")
@click.argument(
    "metadata_path",
    nargs=1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@confirmation_skip_option
@click.pass_context
def dataset_metadata(
    ctx: Context,
    metadata_path: Path,
    yes: bool,
):
    """Validation check for metadata file for DAFNI schema

    Args:
        ctx (Context): contains user session for authentication
        metadata_path (Path): File path to the metadata file
    """
    # Confirm upload details
    arguments = [
        ("metadata path", metadata_path),
    ]
    confirmation_message = "Confirm metadata validation check?"
    argument_confirmation(arguments, confirmation_message, skip=yes)

    # Obtain the metadata
    with open(metadata_path, "r", encoding="utf-8") as metadata_file:
        metadata = json_lib.load(metadata_file)

    # Send to validation endpoint
    click.echo("Validating metadata")
    try:
        validate_metadata(ctx.obj["session"], metadata)
    except ValidationError as err:
        click.echo(err)
        raise SystemExit(1) from err
    click.echo("Metadata validation successful")
