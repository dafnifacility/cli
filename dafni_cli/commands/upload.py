import json as json_lib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import click
from click import Context

from dafni_cli.api.session import DAFNISession
from dafni_cli.commands.helpers import cli_get_latest_dataset_metadata
from dafni_cli.commands.options import (
    confirmation_skip_option,
    dataset_metadata_common_options,
    json_option,
)
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.datasets.dataset_upload import (
    modify_dataset_metadata_for_upload,
    parse_file_names_from_paths,
    upload_dataset,
    upload_dataset_metadata_version,
)
from dafni_cli.models.upload import upload_model
from dafni_cli.utils import argument_confirmation
from dafni_cli.workflows.upload import upload_parameter_set, upload_workflow


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
@confirmation_skip_option
@json_option
@click.pass_context
def model(
    ctx: Context,
    definition: Path,
    image: Path,
    version_message: str,
    parent_id: Optional[str],
    yes: bool,
    json: bool,
):
    """Uploads model to DAFNI from metadata and image files

    Args:
        ctx (Context): contains user session for authentication
        definition (Path): File path to the model definition file
        image (Path): File path to the image file
        version_message (str): Version message to be included with this model version
        parent_id (str): ID of the parent model that this is an update of
        yes (bool): Used to skip confirmations before they are displayed
        json (bool): Whether to print the raw json returned by the DAFNI API
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
    argument_confirmation(
        arguments, confirmation_message, additional_message, skip=yes or json
    )

    upload_model(
        ctx.obj["session"],
        definition_path=definition,
        image_path=image,
        version_message=version_message,
        parent_id=parent_id,
        json=json,
    )


###############################################################################
# COMMAND: Upload a new DATASET to DAFNI
###############################################################################
WILDCARD_HELP_TEXT = (
    "Most terminals also support wildcards for the PATHS parameter e.g. "
    "'data/*' "
    "indicates you wish to upload all files from a folder named 'data'.\n\n"
    "When a folder is found in these paths, all files and folders found "
    "inside will also be uploaded.\n\n"
    "All folders uploaded keep their names in the uploaded file names, e.g. if you "
    "upload an entire folder named 'data' containing a file named 'file1.csv' the "
    "resulting file name will be 'data/file1.csv'."
)


@upload.command(help=f"Upload a new dataset to DAFNI.\n\n{WILDCARD_HELP_TEXT}")
@click.argument(
    "metadata_path",
    nargs=1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.argument(
    "paths",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@confirmation_skip_option
@json_option
@click.pass_context
def dataset(
    ctx: Context,
    metadata_path: Path,
    paths: List[Path],
    yes: bool,
    json: bool,
):
    """Uploads a new Dataset to DAFNI from metadata and dataset files.

    Args:
        ctx (Context): contains user session for authentication
        metadata_path (Path): Dataset metadata file path
        paths (List[Path]): Dataset file/folder paths
        yes (bool): Used to skip confirmations before they are displayed
        json (bool): Whether to print the raw json returned by the DAFNI API
    """
    # Confirm upload details
    arguments = [("Dataset metadata file path", metadata_path)] + [
        ("Dataset file name", file_name)
        for file_name in parse_file_names_from_paths(paths).keys()
    ]
    confirmation_message = "Confirm dataset upload?"
    argument_confirmation(arguments, confirmation_message, skip=yes or json)

    # Obtain the metadata
    with open(metadata_path, "r", encoding="utf-8") as metadata_file:
        metadata = json_lib.load(metadata_file)

    # Upload the dataset
    upload_dataset(ctx.obj["session"], metadata, paths, json=json)


###############################################################################
# COMMAND: Upload a new version of a DATASET to DAFNI
###############################################################################
@upload.command(
    help=f"Upload a new version of a dataset to DAFNI.\n\n{WILDCARD_HELP_TEXT}"
)
@click.argument("existing_version_id", required=True, type=str)
@click.argument(
    "paths",
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
@confirmation_skip_option
@json_option
@click.pass_context
def dataset_version(
    ctx: Context,
    existing_version_id: str,
    paths: List[Path],
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
    yes: bool,
    json: bool,
):
    """Uploads a new version of a Dataset to DAFNI from dataset files

    Args:
        ctx (Context): contains user session for authentication
        existing_version_id (str): Existing version id of the dataset to add a
                                   new version to
        paths (List[Path]): Dataset file/folder paths
        metadata (Optional[Path]): Dataset metadata file
        save (Optional[Path]): Path to save existing metadata in for editing
        yes (bool): Used to skip confirmations before they are displayed
        json (bool): Whether to print the raw json returned by the DAFNI API

        For the rest see dataset_metadata_common_options in options.py
    """

    # We need the version id to get the existing metadata, but the
    # dataset id for the actual upload - instead of requiring both, we look up
    # dataset with the version_id here and obtain both the id and existing
    # metadata once
    dataset_metadata_dict = cli_get_latest_dataset_metadata(
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
            file.write(json_lib.dumps(dataset_metadata_dict, indent=4, sort_keys=True))

        click.echo(f"Saved existing dataset metadata to {save}")
    else:
        # Confirm upload details
        arguments = [
            ("Dataset Title", dataset_metadata_obj.title),
            ("Dataset ID", dataset_metadata_obj.dataset_id),
            ("Dataset Version ID", dataset_metadata_obj.version_id),
        ] + [
            ("Dataset file name", filename)
            for filename in parse_file_names_from_paths(paths).keys()
        ]

        if metadata:
            arguments.append(("Dataset metadata file path", metadata))

        confirmation_message = "Confirm dataset upload?"
        argument_confirmation(arguments, confirmation_message, skip=yes or json)

        # Upload all files
        upload_dataset(
            ctx.obj["session"],
            dataset_id=dataset_metadata_obj.dataset_id,
            metadata=dataset_metadata_dict,
            paths=paths,
            json=json,
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
    "--save",
    type=click.Path(exists=False, path_type=Path),
    default=None,
    help="When given will only save the existing metadata to the specified file allowing it to be modified.",
)
@dataset_metadata_common_options(all_optional=True)
@confirmation_skip_option
@json_option
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
    yes: bool,
    json: bool,
):
    """Uploads a new version of a Dataset's metadata to DAFNI

    Args:
        ctx (Context): contains user session for authentication
        existing_version_id (str): Existing version id of the dataset to add a
                                   new version to
        metadata (Optional[Path]): Dataset metadata file
        save (Optional[Path]): Path to save existing metadata in for editing
        yes (bool): Used to skip confirmations before they are displayed
        json (bool): Whether to print the raw json returned by the DAFNI API

        For the rest see dataset_metadata_common_options in options.py
    """

    # We need the version id to get the existing metadata, but the
    # dataset id for the actual upload - instead of requiring both, we look up
    # dataset with the version_id here and obtain both the id and existing
    # metadata once
    dataset_metadata_dict = cli_get_latest_dataset_metadata(
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
            file.write(json_lib.dumps(dataset_metadata_dict, indent=4, sort_keys=True))

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
        argument_confirmation(arguments, confirmation_message, skip=yes or json)

        # Upload
        upload_dataset_metadata_version(
            ctx.obj["session"],
            dataset_id=dataset_metadata_obj.dataset_id,
            version_id=existing_version_id,
            metadata=dataset_metadata_dict,
            json=json,
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
@confirmation_skip_option
@json_option
@click.pass_context
def workflow(
    ctx: Context,
    definition: Path,
    version_message: str,
    parent_id: str,
    yes: bool,
    json: bool,
):
    """
    Uploads a workflow in JSON form to DAFNI.

    Args:
        ctx (Context): contains user session for authentication
        definition (Path): File path to the workflow definition file
        version_message (str): Version message to be included with this workflow version
        parent_id (str): ID of the parent workflow that this is an update of
        yes (bool): Used to skip confirmations before they are displayed
        json (bool): Whether to print the raw json returned by the DAFNI API
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
    argument_confirmation(
        arguments, confirmation_message, additional_message, skip=yes or json
    )

    upload_workflow(
        ctx.obj["session"], definition, version_message, parent_id, json=json
    )


###############################################################################
# COMMAND: Upload a WORKFLOW PARAMETER SET to DAFNI
###############################################################################
@upload.command(help="Upload a workflow parameter set to DAFNI")
@click.argument(
    "definition", nargs=1, required=True, type=click.Path(exists=True, path_type=Path)
)
@confirmation_skip_option
@json_option
@click.pass_context
def workflow_parameter_set(
    ctx: Context,
    definition: Path,
    yes: bool,
    json: bool,
):
    """Uploads workflow parameter set to DAFNI

    Args:
        ctx (Context): contains user session for authentication
        definition (Path): File path to the parameter set definition file
        yes (bool): Used to skip confirmations before they are displayed
        json (bool): Whether to print the raw json returned by the DAFNI API
    """

    arguments = [
        ("Parameter set definition file path", definition),
    ]
    confirmation_message = "Confirm parameter set upload?"
    argument_confirmation(arguments, confirmation_message, skip=yes or json)

    upload_parameter_set(ctx.obj["session"], definition, json=json)
