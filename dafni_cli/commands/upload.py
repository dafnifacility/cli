import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import click
from click import Context

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.models_api import get_all_models
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import upload_workflow
from dafni_cli.commands.options import dataset_metadata_common_options
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.datasets.dataset_upload import (
    modify_dataset_metadata_for_upload,
    upload_dataset,
    upload_dataset_metadata_version,
)
from dafni_cli.models.upload import upload_model
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
    help="Version message that is to be uploaded with the model.",
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
    parent_id: Optional[str],
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

    upload_model(
        ctx.obj["session"],
        definition_path=definition,
        image_path=image,
        version_message=version_message,
        parent_id=parent_id,
    )


###############################################################################
# COMMAND: Upload a new DATASET to DAFNI
###############################################################################
@upload.command(help="Upload a new dataset to DAFNI")
@click.argument(
    "metadata_path",
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
def dataset(ctx: Context, metadata_path: Path, files: List[Path]):
    """Uploads a new Dataset to DAFNI from metadata and dataset files.

    Args:
        ctx (Context): contains user session for authentication
        metadata_path (Path): Dataset metadata file path
        files (List[Path]): Dataset data files
    """
    # Confirm upload details
    arguments = [("Dataset metadata file path", metadata_path)] + [
        ("Dataset file path", file) for file in files
    ]
    confirmation_message = "Confirm dataset upload?"
    argument_confirmation(arguments, confirmation_message)

    # Obtain the metadata
    with open(metadata_path, "r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    # Upload the dataset
    upload_dataset(ctx.obj["session"], metadata, files)


###############################################################################
# COMMAND: Upload a new version of a DATASET to DAFNI
###############################################################################
@upload.command(help="Upload a new version of a dataset to DAFNI")
@click.argument("existing_version_id", required=True, type=str)
@click.argument(
    "files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--metadata",
    type=click.Path(exists=True, path_type=Path),
    help="Path to a dataset metadata file to upload.",
)
@click.option(
    "--save",
    type=click.Path(exists=False, path_type=Path),
    default=None,
    help="When given will only save the existing metadata to the specified file allowing it to be modified.",
)
@dataset_metadata_common_options(all_optional=True)
@click.pass_context
def dataset_version(
    ctx: Context,
    existing_version_id: str,
    files: List[Path],
    metadata: Optional[Path],
    save: Optional[Path],
    title: Optional[str],
    description: Optional[str],
    identifier: Optional[Tuple[str]],
    subject: Optional[str],
    theme: Optional[Tuple[str]],
    language: Optional[str],
    keyword: Optional[Tuple[str]],
    standard: Optional[Tuple[str, str]],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    organisation: Optional[Tuple[str, str]],
    person: Optional[Tuple[Tuple[str, str]]],
    created_date: Optional[datetime],
    update_frequency: Optional[str],
    publisher: Optional[Tuple[str, str]],
    contact: Optional[Tuple[str, str]],
    license: Optional[str],
    rights: Optional[str],
    version_message: Optional[str],
):
    """Uploads a new version of a Dataset to DAFNI from dataset files

    Args:
        ctx (Context): contains user session for authentication
        existing_version_id (str): Existing version id of the dataset to add a
                                   new version to
        files (List[Path]): Dataset data files
        metadata (Optional[Path]): Dataset metadata file
        save (Optional[Path]): Path to save existing metadata in for editing

        For the rest see dataset_metadata_common_options in options.py
    """

    # We need the version id to get the existing metadata, but the
    # dataset id for the actual upload - instead of requiring both, we look up
    # dataset with the version_id here and obtain both the id and existing
    # metadata once
    dataset_metadata_dict = get_latest_dataset_metadata(
        ctx.obj["session"], existing_version_id
    )
    dataset_metadata_obj = parse_dataset_metadata(dataset_metadata_dict)

    # Load/modify the existing metadata according to the user input
    dataset_metadata_dict = modify_dataset_metadata_for_upload(
        existing_metadata=dataset_metadata_dict,
        metadata_path=metadata,
        title=title,
        description=description,
        subject=subject,
        identifiers=identifier,
        themes=theme,
        language=language,
        keywords=keyword,
        standard=standard,
        start_date=start_date,
        end_date=end_date,
        organisation=organisation,
        people=person,
        created_date=created_date,
        update_frequency=update_frequency,
        publisher=publisher,
        contact=contact,
        license=license,
        rights=rights,
        version_message=version_message,
    )

    if save:
        with open(save, "w", encoding="utf-8") as file:
            file.write(json.dumps(dataset_metadata_dict, indent=4, sort_keys=True))

        click.echo(f"Saved existing dataset metadata to {save}")
    else:
        # Confirm upload details
        arguments = [
            ("Dataset Title", dataset_metadata_obj.title),
            ("Dataset ID", dataset_metadata_obj.dataset_id),
            ("Dataset Version ID", dataset_metadata_obj.version_id),
        ] + [("Dataset file path", file) for file in files]

        if metadata:
            arguments.append(("Dataset metadata file path", metadata))

        confirmation_message = "Confirm dataset upload?"
        argument_confirmation(arguments, confirmation_message)

        # Upload all files
        upload_dataset(
            ctx.obj["session"],
            dataset_id=dataset_metadata_obj.dataset_id,
            metadata=dataset_metadata_dict,
            file_paths=files,
        )


###############################################################################
# COMMAND: Upload a new version of a DATASET's metadata to DAFNI
###############################################################################
@upload.command(help="Upload a new version of a dataset's metadata to DAFNI")
@click.argument("existing_version_id", required=True, type=str)
@click.option(
    "--metadata",
    type=click.Path(exists=True, path_type=Path),
    help="Path to a dataset metadata file to upload.",
)
@click.option(
    "--version-message",
    type=str,
    default=None,
    help="Version message to replace in any existing or provided metadata.",
)
@click.option(
    "--save",
    type=click.Path(exists=False, path_type=Path),
    default=None,
    help="When given will only save the existing metadata to the specified file allowing it to be modified.",
)
@dataset_metadata_common_options(all_optional=True)
@click.pass_context
def dataset_metadata(
    ctx: Context,
    existing_version_id: str,
    metadata: Optional[Path],
    save: Optional[Path],
    title: Optional[str],
    description: Optional[str],
    identifier: Optional[Tuple[str]],
    subject: Optional[str],
    theme: Optional[Tuple[str]],
    language: Optional[str],
    keyword: Optional[Tuple[str]],
    standard: Optional[Tuple[str, str]],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    organisation: Optional[Tuple[str, str]],
    person: Optional[Tuple[Tuple[str, str]]],
    created_date: Optional[datetime],
    update_frequency: Optional[str],
    publisher: Optional[Tuple[str, str]],
    contact: Optional[Tuple[str, str]],
    license: Optional[str],
    rights: Optional[str],
    version_message: Optional[str],
):
    """Uploads a new version of a Dataset's metadata to DAFNI

    Args:
        ctx (Context): contains user session for authentication
        existing_version_id (str): Existing version id of the dataset to add a
                                   new version to
        metadata (Optional[Path]): Dataset metadata file
        save (Optional[Path]): Path to save existing metadata in for editing

        For the rest see dataset_metadata_common_options in options.py
    """

    # We need the version id to get the existing metadata, but the
    # dataset id for the actual upload - instead of requiring both, we look up
    # dataset with the version_id here and obtain both the id and existing
    # metadata once
    dataset_metadata_dict = get_latest_dataset_metadata(
        ctx.obj["session"], existing_version_id
    )
    dataset_metadata_obj = parse_dataset_metadata(dataset_metadata_dict)

    # Load/modify the existing metadata according to the user input
    dataset_metadata_dict = modify_dataset_metadata_for_upload(
        existing_metadata=dataset_metadata_dict,
        metadata_path=metadata,
        title=title,
        description=description,
        subject=subject,
        identifiers=identifier,
        themes=theme,
        language=language,
        keywords=keyword,
        standard=standard,
        start_date=start_date,
        end_date=end_date,
        organisation=organisation,
        people=person,
        created_date=created_date,
        update_frequency=update_frequency,
        publisher=publisher,
        contact=contact,
        license=license,
        rights=rights,
        version_message=version_message,
    )

    if save:
        with open(save, "w", encoding="utf-8") as file:
            file.write(json.dumps(dataset_metadata_dict, indent=4, sort_keys=True))

        click.echo(f"Saved existing dataset metadata to {save}")
    else:
        # Confirm upload details
        arguments = [
            ("Dataset Title", dataset_metadata_obj.title),
            ("Dataset ID", dataset_metadata_obj.dataset_id),
            ("Dataset Version ID", dataset_metadata_obj.version_id),
        ]

        if metadata:
            arguments.append(("Dataset metadata file path", metadata))

        confirmation_message = "Confirm metadata upload?"
        argument_confirmation(arguments, confirmation_message)

        # Upload
        upload_dataset_metadata_version(
            ctx.obj["session"],
            dataset_id=dataset_metadata_obj.dataset_id,
            version_id=existing_version_id,
            metadata=dataset_metadata_dict,
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
    required=True,
    type=str,
    default=None,
    help="Version message that is to be uploaded with the workflow.",
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
    details = upload_workflow(
        ctx.obj["session"], definition, version_message, parent_id
    )

    click.echo("\nUpload successful")
    click.echo(f"Version ID: {details['id']}")
