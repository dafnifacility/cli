from typing import Callable, List, Tuple

import click
from click import Context

from dafni_cli.api.datasets_api import delete_dataset, delete_dataset_version
from dafni_cli.api.models_api import delete_model_version
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import delete_workflow_version
from dafni_cli.commands.helpers import (
    cli_get_latest_dataset_metadata,
    cli_get_model,
    cli_get_workflow,
)
from dafni_cli.datasets.dataset_metadata import DatasetMetadata, parse_dataset_metadata
from dafni_cli.models.model import Model, parse_model
from dafni_cli.utils import argument_confirmation
from dafni_cli.workflows.workflow import parse_workflow


###############################################################################
# Entities
###############################################################################
@click.group(help="Delete an entity from DAFNI")
@click.pass_context
def delete(ctx: Context):
    """Delete entity from DAFNI.

    Args:
        ctx (Context): Context containing the user session.
    """
    ctx.ensure_object(dict)
    ctx.obj["session"] = DAFNISession()


###############################################################################
# Models
###############################################################################
def collate_model_version_details(
    session: DAFNISession, version_ids: Tuple[str]
) -> List[str]:
    """For each given model version, checks for destroy privileges for the
    user and produces a list of the version details of each model to be
    deleted

    Args:
        session (DAFNISession): User session
        version_ids (Tuple[str]): Tuple of the version IDs of each model to be deleted

    Returns:
        List[str]: List of the model details to be displayed during deletion confirmation
    """
    model_version_details_list = []
    for vid in version_ids:
        # Find details of each model version that will be deleted
        model_ver: Model = parse_model(cli_get_model(session, vid))
        # Exit if user doesn't have necessary permissions
        if not model_ver.auth.destroy:
            click.echo(
                "You do not have sufficient permissions to delete model version:"
            )
            click.echo(model_ver.get_version_details())
            raise SystemExit(1)
        model_version_details_list.append(model_ver.get_version_details())
    return model_version_details_list


@delete.command(help="Delete one or more model versions")
@click.argument("version-ids", nargs=-1, required=True, type=str)
@click.pass_context
def model_version(ctx: Context, version_ids: List[str]):
    """
    Delete one or more version(s) of model(s) from DAFNI.

    Args:
        ctx (context): contains user session for authentication
        version_ids (Tuple[str]): ID(s) of the model version(s) to be deleted
    """
    model_version_details_list = collate_model_version_details(
        ctx.obj["session"], version_ids
    )
    argument_confirmation(
        [], "Confirm deletion of model versions?", model_version_details_list
    )
    for vid in version_ids:
        delete_model_version(ctx.obj["session"], vid)
    # Confirm action
    click.echo("Model versions deleted")


###############################################################################
# Datasets
###############################################################################
def _collate_dataset_details(
    session: DAFNISession,
    version_ids: Tuple[str],
    obtain_details: Callable[[DatasetMetadata], str],
    permissions_message: str,
) -> Tuple[List[str], List[str]]:
    """For each given dataset version, checks for destroy privileges for the
    user and produces a list of the details of each dataset to be deleted

    Args:
        session (DAFNISession): User session
        version_ids (Tuple[str]): Tuple of the dataset version IDs of each
                                  dataset to be deleted
        obtain_details (Callable[[DatasetMetadata], str]): Function that
                            returns a string containing relevant details when
                            passed a metadata object
        permissions_message (str): Message to display to the user if they
                            don't have permissions to delete a particular
                            dataset


    Returns:
        List[str]: List of the dataset details to be displayed during deletion
                   confirmation
        List[str]: Dataset IDs that should be deleted
    """
    dataset_details_list = []
    dataset_ids = []
    for vid in version_ids:
        # Find details of each dataset that will be deleted
        dataset_meta: DatasetMetadata = parse_dataset_metadata(
            cli_get_latest_dataset_metadata(session, vid)
        )
        details = obtain_details(dataset_meta)
        # Exit if user doesn't have necessary permissions
        if not dataset_meta.auth.destroy:
            click.echo(permissions_message)
            click.echo(details)
            raise SystemExit(1)
        dataset_details_list.append(details)
        dataset_ids.append(dataset_meta.dataset_id)
    return dataset_details_list, dataset_ids


def collate_dataset_details(
    session: DAFNISession, version_ids: List[str]
) -> Tuple[List[str], List[str]]:
    """For each given dataset, checks for destroy privileges for the
    user and produces a list of the details of each dataset to be deleted

    Args:
        session (DAFNISession): User session
        version_ids (Tuple[str]): Tuple of the dataset version IDs of each
                                  dataset to be deleted

    Returns:
        List[str]: List of the dataset details to be displayed during deletion
                   confirmation
        List[str]: Dataset IDs that should be deleted
    """
    return _collate_dataset_details(
        session=session,
        version_ids=version_ids,
        obtain_details=lambda dataset_meta: dataset_meta.get_details(),
        permissions_message="You do not have sufficient permissions to delete dataset:",
    )


@delete.command(help="Delete one or more datasets")
@click.argument("version-ids", nargs=-1, required=True, type=str)
@click.pass_context
def dataset(ctx: Context, version_ids: Tuple[str]):
    """
    Delete one or more dataset(s) from DAFNI.

    Args:
        ctx (context): contains user session for authentication
        version_ids (Tuple[str]): Version ID(s) of the datasets to be deleted
    """

    # We need the version id to get the metadata, but the dataset id for the
    # actual delete - instead of requiring both, we look up dataset with the
    # version id and obtain both the id and metadata once

    dataset_details_list, dataset_ids = collate_dataset_details(
        ctx.obj["session"], version_ids
    )
    argument_confirmation([], "Confirm deletion of datasets?", dataset_details_list)
    for dataset_id in dataset_ids:
        delete_dataset(ctx.obj["session"], dataset_id)
    # Confirm action
    click.echo("Datasets deleted")


def collate_dataset_version_details(
    session: DAFNISession, version_ids: Tuple[str]
) -> Tuple[List[str], List[str]]:
    """For each given dataset version, checks for destroy privileges for the
    user and produces a list of the version details of each dataset version to
    be deleted

    Args:
        session (DAFNISession): User session
        version_ids (Tuple[str]): Tuple of the dataset version IDs of each
                                  dataset to be deleted

    Returns:
        List[str]: List of the dataset details to be displayed during deletion
                   confirmation
        List[str]: Dataset IDs that should be deleted
    """
    return _collate_dataset_details(
        session=session,
        version_ids=version_ids,
        obtain_details=lambda dataset_meta: dataset_meta.get_version_details(),
        permissions_message="You do not have sufficient permissions to delete dataset version:",
    )


@delete.command(help="Delete one or more dataset versions")
@click.argument("version-ids", nargs=-1, required=True, type=str)
@click.pass_context
def dataset_version(ctx: Context, version_ids: Tuple[str]):
    """
    Delete one or more dataset version(s) from DAFNI.

    Args:
        ctx (context): contains user session for authentication
        version_ids (str): Version ID(s) of the datasets to be deleted
    """

    dataset_details_list, _ = collate_dataset_version_details(
        ctx.obj["session"], version_ids
    )
    argument_confirmation(
        [], "Confirm deletion of dataset versions?", dataset_details_list
    )
    for vid in version_ids:
        delete_dataset_version(ctx.obj["session"], version_id=vid)
    # Confirm action
    click.echo("Dataset versions deleted")


###############################################################################
# Workflows
###############################################################################
def collate_workflow_version_details(
    session: DAFNISession, version_ids: Tuple[str]
) -> List[str]:
    """
    Checks for destroy privileges for the user, and produces a list of the version details
    of each workflow to be deleted

    Args:
        session (DAFNISession): User session
        version_ids (Tuple[str]): List of the version IDs of each workflow to be deleted

    Returns:
        List[str]: List of the workflow  details to be displayed during deletion confirmation
    """
    workflow_version_details_list = []
    for vid in version_ids:
        # Find details of each workflow version that will be deleted
        workflow_ver = parse_workflow(cli_get_workflow(session, vid))
        # Exit if user doesn't have necessary permissions
        if not workflow_ver.auth.destroy:
            click.echo(
                "You do not have sufficient permissions to delete workflow version:"
            )
            click.echo(workflow_ver.get_version_details())
            raise SystemExit(1)
        workflow_version_details_list.append(workflow_ver.get_version_details())
    return workflow_version_details_list


@delete.command(help="Delete one or more workflow versions")
@click.argument("version-ids", nargs=-1, required=True, type=str)
@click.pass_context
def workflow_version(ctx: Context, version_ids: List[str]):
    """
    Delete one or more version(s) of workflow(s) from DAFNI.

    Args:
        ctx (context): contains user session for authentication
        version_ids (Tuple[str]): ID(s) of the workflow version(s) to be deleted
    """
    workflow_version_details_list = collate_workflow_version_details(
        ctx.obj["session"], version_ids
    )
    argument_confirmation(
        [], "Confirm deletion of workflow versions?", workflow_version_details_list
    )
    for vid in version_ids:
        delete_workflow_version(ctx.obj["session"], vid)
    # Confirm action
    click.echo("Workflow versions deleted")
