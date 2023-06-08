from typing import List

import click
from click import Context

from dafni_cli.api.datasets_api import delete_dataset, get_latest_dataset_metadata
from dafni_cli.api.models_api import delete_model, get_model
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import delete_workflow, get_workflow
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
    session: DAFNISession, version_id_list: List[str]
) -> List[str]:
    """
    Checks for destroy privileges for the user, and produces a list of the
    version details of each model to be deleted

    Args:
        session (DAFNISession): User session
        version_id_list (List[str]): List of the version IDs of each model to be deleted

    Returns:
        List[str]: List of the model details to be displayed during deletion confirmation
    """
    model_version_details_list = []
    for vid in version_id_list:
        # Find details of each model version that will be deleted
        model_version: Model = parse_model(get_model(session, vid))
        # Exit if user doesn't have necessary permissions
        if not model_version.auth.destroy:
            click.echo(
                "You do not have sufficient permissions to delete model version:"
            )
            click.echo(model_version.get_version_details())
            raise SystemExit(1)
        model_version_details_list.append(model_version.get_version_details())
    return model_version_details_list


@delete.command(help="Delete one or more model version(s)")
@click.argument("version-id", nargs=-1, required=True, type=str)
@click.pass_context
def model(ctx: Context, version_id: List[str]):
    """
    Delete one or more version(s) of model(s) from DAFNI.

    Args:
        ctx (context): contains user session for authentication
        version_id (str): ID(s) of the model version(s) to be deleted
    """
    model_version_details_list = collate_model_version_details(
        ctx.obj["session"], version_id
    )
    argument_confirmation([], "Confirm deletion of models?", model_version_details_list)
    for vid in version_id:
        delete_model(ctx.obj["session"], vid)
    # Confirm action
    click.echo("Model versions deleted")


###############################################################################
# Datasets
###############################################################################
def collate_dataset_details(
    session: DAFNISession, version_id_list: List[str]
) -> List[str]:
    """
    Checks for destroy privileges for the user, and produces a list of the
    details of each dataset to be deleted

    Args:
        session (DAFNISession): User session
        version_id_list (List[str]): List of the dataset version IDs of each
                                     dataset to be deleted

    Returns:
        List[str]: List of the dataset details to be displayed during deletion
                   confirmation
        List[str]: Dataset IDs that should be deleted
    """
    dataset_details_list = []
    dataset_ids = []
    for did in version_id_list:
        # Find details of each dataset that will be deleted
        dataset_version: DatasetMetadata = parse_dataset_metadata(
            get_latest_dataset_metadata(session, did)
        )
        # Exit if user doesn't have necessary permissions
        if not dataset_version.auth.destroy:
            click.echo("You do not have sufficient permissions to delete dataset:")
            click.echo(dataset_version.get_dataset_details())
            raise SystemExit(1)
        dataset_details_list.append(dataset_version.get_dataset_details())
        dataset_ids.append(dataset_version.dataset_id)
    return dataset_details_list, dataset_ids


@delete.command(help="Delete one or more datasets")
@click.argument("version-id", nargs=-1, required=True, type=str)
@click.pass_context
def dataset(ctx: Context, version_id: List[str]):
    """
    Delete one or more dataset(s) from DAFNI.

    Args:
        ctx (context): contains user session for authentication
        version_id (str): Version ID(s) of the datasets to be deleted
    """

    # We need the version id to get the metadata, but the dataset id for the
    # actual delete - instead of requiring both, we look up dataset with the
    # version_id and obtain both the id and metadata once

    dataset_details_list, dataset_ids = collate_dataset_details(
        ctx.obj["session"], version_id
    )
    argument_confirmation([], "Confirm deletion of datasets?", dataset_details_list)
    for dataset_id in dataset_ids:
        delete_dataset(ctx.obj["session"], dataset_id)
    # Confirm action
    click.echo("Datasets deleted")


###############################################################################
# Workflows
###############################################################################
def collate_workflow_version_details(
    session: DAFNISession, version_id_list: List[str]
) -> List[str]:
    """
    Checks for destroy privileges for the user, and produces a list of the version details
    of each workflow to be deleted

    Args:
        session (DAFNISession): User session
        version_id_list (List[str]): List of the version IDs of each workflow to be deleted

    Returns:
        List[str]: List of the workflow  details to be displayed during deletion confirmation
    """
    workflow_version_details_list = []
    for vid in version_id_list:
        # Find details of each workflow version that will be deleted
        workflow_version = parse_workflow(get_workflow(session, vid))
        # Exit if user doesn't have necessary permissions
        if not workflow_version.auth.destroy:
            click.echo(
                "You do not have sufficient permissions to delete workflow version:"
            )
            click.echo(workflow_version.get_version_details())
            raise SystemExit(1)
        workflow_version_details_list.append(workflow_version.get_version_details())
    return workflow_version_details_list


@delete.command(help="Delete one or more workflow version(s)")
@click.argument("version-id", nargs=-1, required=True, type=str)
@click.pass_context
def workflow(ctx: Context, version_id: List[str]):
    """
    Delete one or more version(s) of workflow(s) from DAFNI.

    Args:
        ctx (context): contains user session for authentication
        version_id (str): ID(s) of the workflow version(s) to be deleted
    """
    workflow_version_details_list = collate_workflow_version_details(
        ctx.obj["session"], version_id
    )
    argument_confirmation(
        [], "Confirm deletion of workflows?", workflow_version_details_list
    )
    for vid in version_id:
        delete_workflow(ctx.obj["session"], vid)
    # Confirm action
    click.echo("Workflow versions deleted")
