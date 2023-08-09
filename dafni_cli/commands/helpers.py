import re
from typing import List, Optional, Tuple

import click

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.api.models_api import get_model
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import get_workflow, get_workflow_instance
from dafni_cli.datasets.dataset_metadata import DataFile, DatasetMetadata
from dafni_cli.workflows.parameter_set import WorkflowParameterSet
from dafni_cli.workflows.workflow import Workflow, parse_workflow


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


def cli_select_dataset_files(
    dataset_metadata: DatasetMetadata,
    file_names: Optional[List[str]],
    file_regex: Optional[str],
) -> List[DataFile]:
    """Returns a list of DataFile's that have file names that match some given
    regex or is one of a list of given file_names

    If both file_regex and file_names are None all of the given datasets files
    will be returned.

    Args:
        file_names (Optional[List[str]]): List of specific file names to select
        file_regex (Optional[str]): Regular expression to match with the names of
                                    the files to select

    Raises:
        SystemExit(1): If file_names is given but not all files are found in
                       the given dataset
    """
    if file_regex is None and file_names is None:
        return dataset_metadata.files

    selected_files = []
    for file in dataset_metadata.files:
        if file_names is not None and file.name in file_names:
            file_names.remove(file.name)
            selected_files.append(file)
        elif file_regex is not None and re.match(file_regex, file.name):
            selected_files.append(file)

    if file_names is not None and len(file_names) > 0:
        click.echo("The following files were not found in the dataset:")
        click.echo("\n".join(file_names))
        raise SystemExit(1)

    return selected_files


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
) -> Tuple[Workflow, WorkflowParameterSet]:
    """Attempts to get a workflow's parameter set with a nice CLI error
    message if it's not found

    Args:
        session (DAFNISession): DAFNISession
        workflow_version_id (str): Version ID of the workflow the parameter
                                   set is found in
        parameter_set_id (str): ID of the parameter set

    Returns:
        Workflow: Workflow with the given version id
        WorkflowParameterSet: Parameter set with the id obtained from the
                              workflow
    """

    workflow_dict = cli_get_workflow(session, workflow_version_id)
    workflow_inst = parse_workflow(workflow_dict)

    try:
        return workflow_inst, workflow_inst.get_parameter_set(parameter_set_id)
    except ResourceNotFoundError as err:
        click.echo(err)
        raise SystemExit(1) from err
