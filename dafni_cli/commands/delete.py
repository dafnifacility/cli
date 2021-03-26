import click
from click import Context
from typing import List

from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.api.models_api import delete_model
from dafni_cli.model.model import Model
from dafni_cli.utils import argument_confirmation


def collate_model_version_details(
        jwt_string: str, version_id_list: List[str]
) -> List[str]:
    """Checks for destroy privileges for the user,
    and produces a list of the version details,
    of each model to be deleted

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
        model_version.get_details_from_id(jwt_string, vid)
        # Exit if user doesn't have necessary permissions
        if not model_version.privileges.destroy:
            click.echo("You do not have sufficient permissions to delete model version:")
            click.echo(model_version.output_version_details())
            exit(1)
        model_version_details_list.append(model_version.output_version_details())
    return model_version_details_list


@click.group()
@click.pass_context
def delete(ctx: Context):
    """Delete entity from DAFNI."""
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


@delete.command(help="Delete one or more model version(s)")
@click.argument(
    "version-id",
    nargs=-1,
    required=True,
    type=str
)
@click.pass_context
def model(ctx: Context, version_id: List[str]):
    """Delete one or more version(s) of model(s) from DAFNI.

    Args:
        ctx (context): contains JWT for authentication
        version_id (str): ID(s) of the model version(s) to be deleted
    """
    model_version_details_list = collate_model_version_details(ctx.obj['jwt'], version_id)
    argument_confirmation(
        [],
        [],
        "Confirm deletion of models?",
        model_version_details_list
    )
    for vid in version_id:
        delete_model(ctx.obj['jwt'], vid)
    # Confirm action
    click.echo("Model versions deleted")
