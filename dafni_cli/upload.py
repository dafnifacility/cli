import click
from click import Context, Path

from dafni_cli.login import check_for_jwt_file
from dafni_cli.api.models_api import (
    validate_model_definition,
    get_model_upload_urls,
    upload_file_to_minio,
    model_ingest,
    model_version_ingest
)


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
@click.argument("--version-message", nargs=1, required=True, type=str)
@click.option("--parent-model", type=str, default=None)
@click.pass_context
def model(
        ctx: Context, definition: str, image: str, version_message: str, parent_model: str
):
    """Uploads model to DAFNI from metadata and image files.
    
    Args:
        ctx (Context): contains JWT for authentication
        definition (str): File path to the model definition file
        image (str): File path to the image file
        version_message (str): Version message to be included with this model version
        parent_model (str): ID of the parent model that this is an update of
    """
    # TODO Confirmation of choices - print name of parent model?

    click.echo("Validating model definition")
    valid, errors = validate_model_definition(ctx.obj["jwt"], definition)
    if not valid:
        click.echo("Definition validation failed with the following errors:", errors)
        exit()

    click.echo("Getting urls")
    upload_id, urls = get_model_upload_urls(ctx.obj["jwt"])
    definition_url = urls["definition"]
    image_url = urls["image"]

    click.echo("Uploading model definition and image")
    upload_file_to_minio(ctx.obj["jwt"], definition_url, definition)
    upload_file_to_minio(ctx.obj["jwt"], image_url, image)

    click.echo("Ingesting model")
    if parent_model:
        model_version_ingest(ctx.obj["jwt"], parent_model, upload_id, version_message)
    else:
        model_ingest(ctx.obj["jwt"], upload_id, version_message)
