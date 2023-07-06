import click

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.api.models_api import get_model
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import get_workflow, get_workflow_instance
from dafni_cli.workflows.workflow import parse_workflow


def cli_get_model(session: DAFNISession, version_id: str) -> dict:
    """Attempts to get a model from a version id with a nice CLI error message
    if it's not found

    Args:
        session (DAFNISession): DAFNISession
        version_id (str): Model version id
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
        version_id (str): Dataset version id
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
        version_id (str): Workflow version id
    """

    try:
        return get_workflow(session, version_id)
    except ResourceNotFoundError as err:
        click.echo(err)
        raise SystemExit(1) from err


def cli_get_workflow_instance(session: DAFNISession, instance_id: str) -> dict:
    """Attempts to get a workflow instance from an instance id with a nice CLI
    error message if it's not found

    Args:
        session (DAFNISession): DAFNISession
        instance_id (str): Workflow instance id
    """

    try:
        return get_workflow_instance(session, instance_id)
    except ResourceNotFoundError as err:
        click.echo(err)
        raise SystemExit(1) from err


def cli_get_workflow_parameter_set(
    session: DAFNISession, workflow_version_id: str, parameter_set_id: str
) -> dict:
    """Attempts to get a workflow's parameter set with a nice CLI error
    message if it's not found

    Args:
        session (DAFNISession): DAFNISession
        workflow_version_id (str): Version ID of the workflow the parameter
                                   set is found in
        parameter_set_id (str): ID of the parameter set
    """

    workflow_dict = cli_get_workflow(session, workflow_version_id)
    workflow_inst = parse_workflow(workflow_dict)

    try:
        return workflow_inst.get_parameter_set(parameter_set_id)
    except ResourceNotFoundError as err:
        click.echo(err)
        raise SystemExit(1) from err
