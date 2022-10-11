import json

import click
from click import Context
from pathlib import Path
from requests.exceptions import HTTPError
from typing import List

from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.api.models_api import (
    validate_model_definition,
    get_model_upload_urls,
    model_version_ingest,
    get_models_dicts
)
from dafni_cli.api.workflows_api import upload_workflow
from dafni_cli.api.minio_api import upload_file_to_minio
from dafni_cli.datasets.dataset_upload import upload_new_dataset_files
from dafni_cli.utils import argument_confirmation


###############################################################################
# COMMAND: Upload an ENTITY to DAFNI
###############################################################################
@click.group(help="Upload an entity to DAFNI")
@click.pass_context
def upload(ctx: Context):
    """Uploads entities (models, datasets, workflows, groups) to DAFNI.
    \f
    Args:
        ctx (Context): Context containing JWT of the user.
    """
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


###############################################################################
# COMMAND: Upload a MODEL to DAFNI
###############################################################################
@upload.command(help="Upload a model to DAFNI")
@click.argument("definition", nargs=1, required=True, type=click.Path(exists=True))
@click.argument("image", nargs=1, required=True, type=click.Path(exists=True))
@click.option(
    "--version-message",
    "-m",
    nargs=1,
    required=True,
    help="Version message that is to be uploaded with the version. Required.",
    type=str,
)
@click.option(
    "--parent-id",
    type=str,
    help="Parent ID of the parent model if this is an updated version of an existing model",
    default=None,
)
@click.pass_context
def model(
    ctx: Context,
    definition: click.Path,
    image: click.Path,
    version_message: str,
    parent_id: str,
):
    """Uploads model to DAFNI from metadata and image files.
    \f
    Args:
        ctx (Context): contains JWT for authentication
        definition (click.Path): File path to the model definition file
        image (click.Path): File path to the image file
        version_message (str): Version message to be included with this model version
        parent_id (str): ID of the parent model that this is an update of
    """
    argument_names = [
        "Model definition file path",
        "Image file path",
        "Version message",
    ]
    arguments = [definition, image, version_message]
    confirmation_message = "Confirm model upload?"
    if parent_id:
        argument_names.append("Parent model ID")
        arguments.append(parent_id)
        additional_message = None
    else:
        additional_message = ["No parent model: new model to be created"]
    argument_confirmation(
        argument_names, arguments, confirmation_message, additional_message
    )

    click.echo("Validating model definition")
    # Print helpful message when 500 error returned
    try:
        valid, error_message = validate_model_definition(ctx.obj["jwt"], definition)
    except HTTPError as e:
        if e.response.status_code == 500:
            click.echo(
                "Error validating the model definition. "
                "See https://docs.secure.dafni.rl.ac.uk/docs/how-to/models/how-to-write-a-model-definition-file/"
                " for guidance"
            )
        else:
            click.echo(e)
        raise SystemExit(1)
    if not valid:
        click.echo(
            "Definition validation failed with the following errors: " + error_message
        )
        raise SystemExit(1)

    click.echo("Getting urls")
    upload_id, urls = get_model_upload_urls(ctx.obj["jwt"])
    definition_url = urls["definition"]
    image_url = urls["image"]

    click.echo("Uploading model definition and image")
    upload_file_to_minio(ctx.obj["jwt"], definition_url, definition)
    upload_file_to_minio(ctx.obj["jwt"], image_url, image)

    click.echo("Ingesting model")
    model_version_ingest(ctx.obj["jwt"], upload_id, version_message, parent_id)

    click.echo("Model upload complete")


###############################################################################
# COMMAND: Upload a DATASET to DAFNI
###############################################################################
@upload.command(help="Upload a dataset to DAFNI")
@click.argument("definition", nargs=1, required=True, type=click.Path(exists=True))
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def dataset(ctx: Context, definition: click.Path, files: List[click.Path]):
    """Uploads a Dataset to DAFNI from metadata and dataset files.
    \f
    Args:
        ctx (Context): contains JWT for authentication
        definition (click.Path): Dataset metadata file
        files (List[click.Path]): Dataset data files
    """
    # Confirm upload details
    argument_names = ["Dataset definition file path"] + [
        "Dataset file path" for file_path in files
    ]
    arguments = [definition, *files]
    confirmation_message = "Confirm Dataset upload?"
    argument_confirmation(argument_names, arguments, confirmation_message)

    # Upload all files
    upload_new_dataset_files(ctx.obj["jwt"], definition, files)


###############################################################################
# COMMAND: Upload a WORKFLOW to DAFNI
###############################################################################
@upload.command(help="Upload a workflow to DAFNI")
@click.argument("definition", nargs=1, required=True, type=click.Path(exists=True))
@click.option(
    "--version-message",
    "-m",
    nargs=1,
    required=False,
    type=str,
    default=None,
    help="Message describing this version, will override any version message that is defined in the workflow description"
)
@click.option(
    "--parent-id",
    nargs=1,
    required=False,
    type=str,
    default=None,
    help="Parent workflow ID if this is an updated version of an existing workflow"
)
@click.pass_context
def workflow(
    ctx: Context,
    definition: click.Path,
    version_message: str,
    parent_id: str,
):
    """
    Uploads a workflow in JSON form to DAFNI.
    \f
    Args:
        ctx (Context): contains JWT for authentication
        definition (click.Path): File path to the workflow definition file
        version_message (str): Version message to be included with this workflow version
        parent_id (str): ID of the parent workflow that this is an update of
    """
    argument_names = [
        "Workflow definition file path",
        "Version message",
    ]
    arguments = [definition, version_message]
    confirmation_message = "Confirm workflow upload?"
    if parent_id:
        argument_names.append("Parent workflow ID")
        arguments.append(parent_id)
        additional_message = None
    else:
        additional_message = ["No parent workflow: new workflow to be created"]
    argument_confirmation(
        argument_names, arguments, confirmation_message, additional_message
    )

    click.echo("Validating workflow definition")
    # Print helpful message when 500 error returned
    #try:
    #    valid, error_message = validate_model_definition(ctx.obj["jwt"], definition)
    #except HTTPError as e:
    #    if e.response.status_code == 500:
    #        click.echo(
    #            "Error validating the model definition. "
    #            "See https://docs.secure.dafni.rl.ac.uk/docs/how-to/models/how-to-write-a-model-definition-file/"
    #            " for guidance"
    #        )
    #    else:
    #        click.echo(e)
    #    raise SystemExit(1)
    #if not valid:
    #    click.echo(
    #        "Definition validation failed with the following errors: " + error_message
    #    )
    #    raise SystemExit(1)

    #click.echo("Getting urls")
    #upload_id, urls = get_model_upload_urls(ctx.obj["jwt"])
    #definition_url = urls["definition"]

    #click.echo("Uploading model definition and image")
    #upload_file_to_minio(ctx.obj["jwt"], definition_url, definition)

    #click.echo("Ingesting model")
    #model_version_ingest(ctx.obj["jwt"], upload_id, version_message, parent_model)

    click.echo("Uploading workflow")
    upload_workflow(ctx.obj["jwt"], definition, version_message, parent_id)

    click.echo("Workflow upload complete")


###############################################################################
# TODO - WIP
@upload.command(help="Upload a parameterised workflow to DAFNI")
@click.argument("definition", nargs=1, required=True, type=click.Path(exists=True))
#@click.argument("image", nargs=1, required=True, type=click.Path(exists=True))
@click.option(
    "--version-message",
    "-m",
    nargs=1,
    required=True,
    help="Version message that is to be uploaded with the version. Required.",
    type=str,
)
@click.option(
    "--parent-id",
    type=str,
    help="Parent workflow ID if this is an updated version of an existing workflow",
    default=None,
)
@click.pass_context
def workflow_params(
    ctx: Context,
    definition: click.Path,
    version_message: str,
    parent_id: str,
):
    """
    Uploads a workflow in JSON form to DAFNI.
    \f
    Args:
        ctx (Context): contains JWT for authentication
        definition (click.Path): File path to the workflow definition file
        version_message (str): Version message to be included with this model version
        parent_model (str): ID of the parent model that this is an update of
    """
    argument_names = [
        "Workflow definition file path",
        "Version message",
    ]
    arguments = [definition, version_message]
    confirmation_message = "Confirm workflow upload?"
    if parent_id:
        argument_names.append("Parent workflow ID")
        arguments.append(parent_id)
        additional_message = None
    else:
        additional_message = ["No parent workflow: new workflow to be created"]
    argument_confirmation(
        argument_names, arguments, confirmation_message, additional_message
    )

    click.echo("Validating workflow definition")
    with open(definition, "r") as f:
        workflow_description = json.load(f)
    model_list = get_models_dicts(ctx.obj["jwt"])
    for step in definition.spec:
        pass

    click.echo("Uploading workflow")
    upload_workflow(ctx.obj["jwt"], workflow_description)

    click.echo("Workflow upload complete")
# TODO: WIP
###############################################################################
