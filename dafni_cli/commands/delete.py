import click
from click import Context
from typing import List

from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.api.models_api import delete_model
from dafni_cli.model.model import Model
from dafni_cli.utils import argument_confirmation


def collate_model_version_details(ctx: Context, version_id_list: List[str]) -> List[str]:
    model_version_details_list = []
    for vid in version_id_list:
        # Find name (and version message) of each model version that will be deleted
        model_version = Model(vid)
        model_version.get_details_from_id(ctx.obj['jwt'], vid)
        if not model_version.privileges.destroy:
            click.echo("You do not have sufficient permissions to delete model version:")
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
    model_version_details_list = collate_model_version_details(ctx, version_id)
    argument_confirmation(
        model_version_details_list,
        [""] * len(model_version_details_list),
        "Confirm deletion of models?"
    )
    for vid in version_id:
        delete_model(ctx.obj['jwt'], vid)
    # Confirm action
    click.echo("Model versions deleted")
