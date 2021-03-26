import click
from click import Context
from click.testing import CliRunner
from pathlib import Path
from requests.exceptions import HTTPError
from requests import Response

from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.api.models_api import (
    validate_model_definition,
    get_model_upload_urls,
    upload_file_to_minio,
    model_version_ingest
)
from dafni_cli.utils import argument_confirmation


@click.group()
@click.pass_context
def upload(ctx: Context):
    """Uploads entities (models, datasets, workflows, groups) to DAFNI.

    Args:
        ctx (Context): Context containing JWT of the user.
    """
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


@upload.command()
@click.argument("definition", nargs=1, required=True, type=click.Path(exists=True))
@click.argument("image", nargs=1, required=True, type=click.Path(exists=True))
@click.option("--version-message", nargs=1, required=True, type=str)
@click.option("--parent-model", type=str, default=None)
@click.pass_context
def model(
        ctx: Context, definition: click.Path, image: click.Path, version_message: str, parent_model: str
):
    """Uploads model to DAFNI from metadata and image files.
    
    Args:
        ctx (Context): contains JWT for authentication
        definition (click.Path): File path to the model definition file
        image (click.Path): File path to the image file
        version_message (str): Version message to be included with this model version
        parent_model (str): ID of the parent model that this is an update of
    """
    argument_names = ["Model definition file path",
                      "Image file path",
                      "Version message"]
    arguments = [definition,
                 image,
                 version_message]
    confirmation_message = "Confirm model upload?"
    if parent_model:
        argument_names.append("Parent model ID")
        arguments.append(parent_model)
        additional_message = None
    else:
        additional_message = ["No parent model: new model to be created"]
    argument_confirmation(argument_names, arguments, confirmation_message, additional_message)

    click.echo("Validating model definition")
    # Print helpful message when 500 error returned
    try:
        valid, error_message = validate_model_definition(ctx.obj["jwt"], definition)
    except HTTPError as e:
        if e.response.status_code == 500:
            click.echo("Error validating the model definition. "
                       "See https://docs.secure.dafni.rl.ac.uk/docs/how-to/models/how-to-write-a-model-definition-file/"
                       " for guidance")
        else:
            click.echo(e)
        exit(1)
    if not valid:
        click.echo("Definition validation failed with the following errors: " + error_message)
        exit(1)

    click.echo("Getting urls")
    upload_id, urls = get_model_upload_urls(ctx.obj["jwt"])
    definition_url = urls["definition"]
    image_url = urls["image"]

    click.echo("Uploading model definition and image")
    upload_file_to_minio(ctx.obj["jwt"], definition_url, definition)
    upload_file_to_minio(ctx.obj["jwt"], image_url, image)

    click.echo("Ingesting model")
    model_version_ingest(ctx.obj["jwt"], upload_id, version_message, parent_model)

    click.echo("Model upload complete")
