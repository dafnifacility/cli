import json
from pathlib import Path
from typing import List, Optional

import click
from requests.exceptions import HTTPError

from dafni_cli.api.exceptions import DAFNIError, EndpointNotFoundError
from dafni_cli.api.minio_api import (
    create_temp_bucket,
    delete_temp_bucket,
    get_data_upload_urls,
    upload_dataset_metadata,
    upload_file_to_minio,
)
from dafni_cli.api.session import DAFNISession


def upload_new_dataset_files(
    session: DAFNISession, definition_path: Path, file_paths: List[Path]
) -> None:
    """Function to upload all files associated with a new Dataset

    Args:
        session (DAFNISession): User session
        definition_path (Path): Path to Dataset metadata file
        file_paths (List[Path]): List of Paths to dataset data files
    """

    click.echo("\nRetrieving temporary bucket ID")
    temp_bucket_id = create_temp_bucket(session)

    # If any exception happens now, we want to make sure we delete the
    # temporary bucket to prevent a build up in the user's quota
    try:
        # Upload all files
        upload_files(session, temp_bucket_id, file_paths)
        with open(definition_path, "r", encoding="utf-8") as definition_file:
            details = upload_metadata(
                session, json.load(definition_file), temp_bucket_id
            )
    except BaseException:
        click.echo("Deleting temporary bucket")
        delete_temp_bucket(session, temp_bucket_id)
        raise

    # Output Details
    click.echo("\nUpload successful")
    click.echo(f"Dataset ID: {details['datasetId']}")
    click.echo(f"Version ID: {details['versionId']}")
    click.echo(f"Metadata ID: {details['metadataId']}")


def remove_dataset_metadata_invalid_for_upload(metadata: dict):
    """Function to remove metadata for a dataset that is given when getting it
    but are not valid during upload

    Args:
        metadata (dict): The metadata to modify
    """

    del metadata["@id"]
    del metadata["dct:issued"]
    del metadata["dct:modified"]
    del metadata["mediatypes"]
    del metadata["version_history"]
    del metadata["auth"]
    del metadata["dcat:distribution"]


def modify_dataset_metadata_for_upload(
    existing_metadata: dict,
    definition_path: Optional[Path],
    version_message: Optional[str],
) -> dict:
    """Modifies existing dataset metadata or that loaded from a file according
    to user specified parameters and in a format ready for upload

    Args:
        existing_metadata (dict): Dictionary of existing metadata from the API
        definition_path (Optional[Path]): Path to a Dataset metadata file.
                        When None will use the existing_metadata instead but
                        will delete any keys invalid for upload.
        version_message (Optional[str]): Version message - Will replace
                        whatever already exists in the loaded metadata
    Returns:
        dict: The modified dataset metadata
    """

    # Load the metadata from the definition file if present, or otherwise
    # use the existing but remove parts invalid for reupload
    if definition_path:
        with open(definition_path, "r", encoding="utf-8") as definition_file:
            metadata = json.load(definition_file)
    else:
        metadata = existing_metadata.copy()
        remove_dataset_metadata_invalid_for_upload(metadata)

    # Make modifications to the metadata from the inputs
    if version_message:
        # TODO: Find a more robust solution for this - could reparse from the
        # structures using existing definitions?
        metadata["dafni_version_note"] = version_message

    return metadata


def upload_dataset_version(
    session: DAFNISession,
    dataset_id: str,
    metadata: dict,
    file_paths: List[Path],
) -> None:
    """Function to upload all files associated with a new Dataset

    Args:
        session (DAFNISession): User session
        dataset_id (str): ID of the existing dataset to add a version to
        metadata (dict): Metadata to upload
        file_paths (List[Path]): List of Paths to dataset data files
    """

    click.echo("\nRetrieving temporary bucket ID")
    temp_bucket_id = create_temp_bucket(session)

    # If any exception happens now, we want to make sure we delete the
    # temporary bucket to prevent a build up in the user's quota
    try:
        # Upload all files
        upload_files(session, temp_bucket_id, file_paths)
        details = upload_metadata(
            session, metadata, temp_bucket_id, dataset_id=dataset_id
        )
    except BaseException:
        click.echo("Deleting temporary bucket")
        delete_temp_bucket(session, temp_bucket_id)
        raise

    # Output Details
    click.echo("\nUpload successful")
    click.echo(f"Dataset ID: {details['datasetId']}")
    click.echo(f"Version ID: {details['versionId']}")
    click.echo(f"Metadata ID: {details['metadataId']}")


def upload_files(session: DAFNISession, temp_bucket_id: str, file_paths: List[Path]):
    """Function to upload all given files to a temporary bucket via the Minio
    API

    Args:
        session (DAFNISession): User session
        temp_bucket_id (str): Minio temporary bucket ID to upload files to
        file_paths (List[Path]): List of Paths to dataset data files
    """
    click.echo("Retrieving file upload URls")
    file_names = {file_path.name: file_path for file_path in file_paths}
    upload_urls = get_data_upload_urls(session, temp_bucket_id, list(file_names.keys()))

    click.echo("Uploading files")
    for key, value in upload_urls["URLs"].items():
        upload_file_to_minio(session, value, file_names[key])


def upload_metadata(
    session: DAFNISession,
    metadata: dict,
    temp_bucket_id: str,
    dataset_id: Optional[str] = None,
) -> dict:
    """Function to upload the Metadata to the Minio API, with the
    given Minio Temporary Upload ID

    Deletes the temporary upload bucket if unsuccessful to avoid
    any unnecessary build up

    Args:
        session ([type]): User session
        metadata (dict): The metadata to upload
        temp_bucket_id (str): Minio Temporary Bucket ID
        dataset_id (str): ID of an existing dataset to upload the metadata to

    Returns:
        dict: Upload response in json format
    """
    click.echo("Uploading metadata file")
    try:
        response = upload_dataset_metadata(
            session, temp_bucket_id, metadata, dataset_id=dataset_id
        )
    except (EndpointNotFoundError, DAFNIError, HTTPError) as err:
        click.echo(f"\nMetadata upload failed: {err}")

        raise SystemExit(1) from err

    return response
