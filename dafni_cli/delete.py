import click
from click import Context

from dafni_cli.login import check_for_jwt_file
from dafni_cli.api.models_api import delete_model
from dafni_cli.model.model import Model
from dafni_cli.consts import TAB_SPACE


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
def model(ctx: Context, version_id: str):
    """Delete one or more version(s) of model(s) from DAFNI.

    Args:
        ctx (context): contains JWT for authentication
        version_id (str): ID(s) of the model version(s) to be deleted
    """
    click.echo("Are you sure you would like to delete the following model versions?:")
    for vid in version_id:
        # Find name (and version message) of each model version that will be deleted
        model_version = Model(vid)
        model_version.get_details_from_id(ctx.obj['jwt'], vid)
        if not model_version.dictionary['auth']['destroy']:
            click.echo("You do not have sufficient permissions to delete model version:")
        click.echo("ID: " +
                   vid +
                   TAB_SPACE +
                   "Name: " +
                   model_version.display_name +
                   TAB_SPACE +
                   "Publication date: " +
                   model_version.publication_time.date().strftime("%B %d %Y") +
                   TAB_SPACE +
                   "Version message: " +
                   model_version.version_message
                   )
        if not model_version.dictionary['auth']['destroy']:
            exit(1)
    # Ask for confirmation
    click.confirm("", abort=True)
    for vid in version_id:
        delete_model(ctx.obj['jwt'], vid)
    # Confirm action
    click.echo("Model versions deleted")
