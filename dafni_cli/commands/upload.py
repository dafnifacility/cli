import json
from pathlib import Path
from typing import List, Optional

import click
from click import Context

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.exceptions import ValidationError
from dafni_cli.api.minio_api import upload_file_to_minio
from dafni_cli.api.models_api import (
    get_all_models,
    get_model_upload_urls,
    model_version_ingest,
    validate_model_definition,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import upload_workflow
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.datasets.dataset_upload import (
    upload_dataset_version,
    upload_new_dataset_files,
)
from dafni_cli.utils import argument_confirmation


###############################################################################
# COMMAND: Upload an ENTITY to DAFNI
###############################################################################
@click.group(help="Upload an entity to DAFNI")
@click.pass_context
def upload(ctx: Context):
    """Uploads entities (models, datasets, workflows, groups) to DAFNI.

    Args:
        ctx (Context): Context containing the user session.
    """
    ctx.ensure_object(dict)
    ctx.obj["session"] = DAFNISession()


###############################################################################
# COMMAND: Upload a MODEL to DAFNI
###############################################################################
@upload.command(help="Upload a model to DAFNI")
@click.argument(
    "definition", nargs=1, required=True, type=click.Path(exists=True, path_type=Path)
)
@click.argument(
    "image", nargs=1, required=True, type=click.Path(exists=True, path_type=Path)
)
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
    definition: Path,
    image: Path,
    version_message: str,
    parent_id: str,
):
    """Uploads model to DAFNI from metadata and image files

    Args:
        ctx (Context): contains user session for authentication
        definition (Path): File path to the model definition file
        image (Path): File path to the image file
        version_message (str): Version message to be included with this model version
        parent_id (str): ID of the parent model that this is an update of
    """
    arguments = [
        ("Model definition file path", definition),
        ("Image file path", image),
        ("Version message", version_message),
    ]
    confirmation_message = "Confirm model upload?"
    if parent_id:
        arguments.append(("Parent model ID", parent_id))
        additional_message = None
    else:
        additional_message = ["No parent model: New model to be created"]
    argument_confirmation(arguments, confirmation_message, additional_message)

    click.echo("Validating model definition")
    try:
        validate_model_definition(ctx.obj["session"], definition)
    except ValidationError as err:
        click.echo(err)

        raise SystemExit(1) from err

    click.echo("Getting urls")
    upload_id, urls = get_model_upload_urls(ctx.obj["session"])
    definition_url = urls["definition"]
    image_url = urls["image"]

    click.echo("Uploading model definition and image")
    upload_file_to_minio(ctx.obj["session"], definition_url, definition)
    upload_file_to_minio(ctx.obj["session"], image_url, image)

    click.echo("Ingesting model")
    model_version_ingest(ctx.obj["session"], upload_id, version_message, parent_id)

    click.echo("Model upload complete")


###############################################################################
# COMMAND: Upload a new DATASET to DAFNI
###############################################################################
@upload.command(help="Upload a new dataset to DAFNI")
@click.argument(
    "definition",
    nargs=1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.argument(
    "files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.pass_context
def dataset(ctx: Context, definition: Path, files: List[Path]):
    """Uploads a new Dataset to DAFNI from metadata and dataset files.

    Args:
        ctx (Context): contains user session for authentication
        definition (Path): Dataset metadata file
        files (List[Path]): Dataset data files
    """
    # Confirm upload details
    arguments = [("Dataset definition file path", definition)] + [
        ("Dataset file path", file) for file in files
    ]
    confirmation_message = "Confirm dataset upload?"
    argument_confirmation(arguments, confirmation_message)

    # Upload all files
    upload_new_dataset_files(ctx.obj["session"], definition, files)


###############################################################################
# COMMAND: Upload a new version of a DATASET to DAFNI
###############################################################################
@upload.command(help="Upload a new version of a dataset to DAFNI")
@click.argument("version_id", required=True, type=str)
@click.argument(
    "files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--definition",
    type=click.Path(exists=True, path_type=Path),
    help="Path to a dataset metadata definition file to upload",
)
@click.option(
    "--version-message",
    type=str,
    default=None,
    help="Version message to replace in any existing or provided metadata",
)
@click.pass_context
def dataset_version(
    ctx: Context,
    version_id: str,
    files: List[Path],
    definition: Optional[Path],
    version_message: Optional[str],
):
    """Uploads a new version of a Dataset to DAFNI from dataset files

    Args:
        ctx (Context): contains user session for authentication
        version_id (str): Existing version id of the dataset to add a new
                          version too
        files (List[Path]): Dataset data files
        definition (Path): Dataset metadata file
        version_message (str): Version message
    """

    # We need the version id to get the existing metadata, but the
    # dataset id for the actual upload - instead of requiring both, we look up
    # dataset with the version_id here and obtain both the id and existing
    # metadata once
    dataset_metadata_dict = get_latest_dataset_metadata(ctx.obj["session"], version_id)
    dataset_metadata = parse_dataset_metadata(dataset_metadata_dict)

    # Confirm upload details
    arguments = [
        ("Dataset Title", dataset_metadata.title),
        ("Dataset ID", dataset_metadata.dataset_id),
        ("Dataset Version ID", dataset_metadata.version_id),
    ] + [("Dataset file path", file) for file in files]

    if definition:
        arguments.append(("Dataset definition file path", definition))

    confirmation_message = "Confirm dataset upload?"
    argument_confirmation(arguments, confirmation_message)

    # Upload all files
    upload_dataset_version(
        ctx.obj["session"],
        dataset_id=dataset_metadata.dataset_id,
        existing_metadata=dataset_metadata_dict,
        file_paths=files,
        definition_path=definition,
        version_message=version_message,
    )


###############################################################################
# COMMAND: Upload a WORKFLOW to DAFNI
###############################################################################
@upload.command(help="Upload a workflow to DAFNI")
@click.argument(
    "definition", nargs=1, required=True, type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--version-message",
    "-m",
    nargs=1,
    required=False,
    type=str,
    default=None,
    help="Message describing this version, will override any version message that is defined in the workflow description",
)
@click.option(
    "--parent-id",
    nargs=1,
    required=False,
    type=str,
    default=None,
    help="Parent workflow ID if this is an updated version of an existing workflow",
)
@click.pass_context
def workflow(
    ctx: Context,
    definition: Path,
    version_message: str,
    parent_id: str,
):
    """
    Uploads a workflow in JSON form to DAFNI.

    Args:
        ctx (Context): contains user session for authentication
        definition (Path): File path to the workflow definition file
        version_message (str): Version message to be included with this workflow version
        parent_id (str): ID of the parent workflow that this is an update of
    """
    arguments = [
        ("Workflow definition file path", definition),
        ("Version message", version_message),
    ]
    confirmation_message = "Confirm workflow upload?"
    if parent_id:
        arguments.append(("Parent workflow ID", parent_id))
        additional_message = None
    else:
        additional_message = ["No parent workflow: new workflow to be created"]
    argument_confirmation(arguments, confirmation_message, additional_message)

    # TODO: Validate workflow definition using workflows/validate?

    click.echo("Uploading workflow")
    upload_workflow(ctx.obj["session"], definition, version_message, parent_id)

    click.echo("Workflow upload complete")


###############################################################################
# TODO - WIP
@upload.command(help="Upload a parameterised workflow to DAFNI")
@click.argument(
    "definition", nargs=1, required=True, type=click.Path(exists=True, path_type=Path)
)
# @click.argument("image", nargs=1, required=True, type=click.Path(exists=True, path_type=Path))
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
    definition: Path,
    version_message: str,
    parent_id: str,
):
    """
    Uploads a workflow in JSON form to DAFNI.

    Args:
        ctx (Context): contains user session for authentication
        definition (Path): File path to the workflow definition file
        version_message (str): Version message to be included with this model version
        parent_model (str): ID of the parent model that this is an update of
    """
    arguments = [
        ("Workflow definition file path", definition),
        ("Version message", version_message),
    ]
    confirmation_message = "Confirm workflow upload?"
    if parent_id:
        arguments.append(("Parent workflow ID", parent_id))
        additional_message = None
    else:
        additional_message = ["No parent workflow: new workflow to be created"]
    argument_confirmation(arguments, confirmation_message, additional_message)

    click.echo("Validating workflow definition")
    with open(definition, "r") as f:
        workflow_description = json.load(f)
    model_list = get_all_models(ctx.obj["session"])
    for step in definition.spec:
        pass

    click.echo("Uploading workflow")
    upload_workflow(ctx.obj["session"], workflow_description)

    click.echo("Workflow upload complete")


# TODO: WIP
###############################################################################
