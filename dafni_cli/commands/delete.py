import click
from click import Context
from typing import List

from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.api.models_api import delete_model
from dafni_cli.model.model import Model
from dafni_cli.api.workflows_api import delete_workflow
from dafni_cli.workflow.workflow import Workflow
from dafni_cli.utils import argument_confirmation


###############################################################################
# Entities
###############################################################################
@click.group(help="Delete an entity from DAFNI")
@click.pass_context
def delete(ctx: Context):
    """Delete entity from DAFNI.
    \f
    Args:
        ctx (Context): Context containing JWT of the user.
    """
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


###############################################################################
# Models
###############################################################################
def collate_model_version_details(jwt_string: str, version_id_list: List[str]) -> List[str]:
    """
    Checks for destroy privileges for the user, and produces a list of the
    version details of each model to be deleted

    Args:
        jwt_string (str): JWT
        version_id_list (List[str]): List of the version IDs of each model to be deleted

    Returns:
        List[str]: List of the model details to be displayed during deletion confirmation
    """
    model_version_details_list = []
    for vid in version_id_list:
        # Find details of each model version that will be deleted
        model_version = Model(vid)
        model_version.get_attributes_from_id(jwt_string, vid)
        # Exit if user doesn't have necessary permissions
        if not model_version.auth.destroy:
            click.echo(
                "You do not have sufficient permissions to delete model version:"
            )
            click.echo(model_version.output_version_details())
            raise SystemExit(1)
        model_version_details_list.append(model_version.output_version_details())
    return model_version_details_list


@delete.command(help="Delete one or more model version(s)")
@click.argument("version-id", nargs=-1, required=True, type=str)
@click.pass_context
def model(ctx: Context, version_id: List[str]):
    """
    Delete one or more version(s) of model(s) from DAFNI.
    \f
    Args:
        ctx (context): contains JWT for authentication
        version_id (str): ID(s) of the model version(s) to be deleted
    """
    model_version_details_list = collate_model_version_details(
        ctx.obj["jwt"], version_id
    )
    argument_confirmation(
        [], [], "Confirm deletion of models?", model_version_details_list
    )
    for vid in version_id:
        delete_model(ctx.obj["jwt"], vid)
    # Confirm action
    click.echo("Model versions deleted")


###############################################################################
# Workflows
###############################################################################
def collate_workflow_version_details(
    jwt_string: str, version_id_list: List[str]
) -> List[str]:
    """
    Checks for destroy privileges for the user, and produces a list of the version details
    of each workflow to be deleted

    Args:
        jwt_string (str): JWT
        version_id_list (List[str]): List of the version IDs of each workflow to be deleted

    Returns:
        List[str]: List of the worfflow  details to be displayed during deletion confirmation
    """
    workflow_version_details_list = []
    for vid in version_id_list:
        # Find details of each workflow version that will be deleted
        workflow_version = Workflow(vid)
        workflow_version.get_attributes_from_id(jwt_string, vid)
        # Exit if user doesn't have necessary permissions
        if not workflow_version.auth.destroy:
            click.echo(
                "You do not have sufficient permissions to delete workflow version:"
            )
            click.echo(workflow_version.output_version_details())
            raise SystemExit(1)
        workflow_version_details_list.append(workflow_version.output_version_details())
    return workflow_version_details_list


@delete.command(help="Delete one or more workflow version(s)")
@click.argument("version-id", nargs=-1, required=True, type=str)
@click.pass_context
def workflow(ctx: Context, version_id: List[str]):
    """
    Delete one or more version(s) of workflow(s) from DAFNI.
    \f
    Args:
        ctx (context): contains JWT for authentication
        version_id (str): ID(s) of the model version(s) to be deleted
    """
    workflow_version_details_list = collate_workflow_version_details(
        ctx.obj["jwt"], version_id
    )
    argument_confirmation(
        [], [], "Confirm deletion of models?", workflow_version_details_list
    )
    for vid in version_id:
        delete_workflow(ctx.obj["jwt"], vid)
    # Confirm action
    click.echo("Workflow versions deleted")