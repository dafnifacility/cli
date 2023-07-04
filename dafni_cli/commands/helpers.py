import click
from click import Context

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.api.models_api import get_model
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import get_workflow


def cli_get_model(session: DAFNISession, version_id: str) -> dict:
    """Attempts to get a model from a version id with a nice CLI error message
    if it's not found

    Args:
        session (DAFNISession): DAFNISession
        version_id (version_id): Model version id
    """

    try:
        return get_model(session, version_id)
    except ResourceNotFoundError as err:
        click.echo(err)
        raise SystemExit(1) from err


def cli_get_latest_dataset_metadata(session: DAFNISession, version_id: str) -> dict:
    """Attempts to get a dataset's metadata from a version id with a nice CLI
    error message if it's not found

    Args:
        session (DAFNISession): DAFNISession
        version_id (version_id): Dataset version id
    """

    try:
        return get_latest_dataset_metadata(session, version_id)
    except ResourceNotFoundError as err:
        click.echo(err)
        raise SystemExit(1) from err


def cli_get_workflow(session: DAFNISession, version_id: str) -> dict:
    """Attempts to get a workflow from a version id with a nice CLI error
    message if it's not found

    Args:
        session (DAFNISession): DAFNISession
        version_id (version_id): Workflow version id
    """

    try:
        return get_workflow(session, version_id)
    except ResourceNotFoundError as err:
        click.echo(err)
        raise SystemExit(1) from err
