import json
from os.path import basename, normpath
from typing import List

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
    session: DAFNISession, definition: click.Path, files: List[click.Path]
) -> None:
    """Function to upload all files associated with a new Dataset

    Args:
        session (DAFNISession): User session
        definition (click.Path): Path to Dataset metadata file
        files (List[click.Path]): List of Paths to dataset data files
    """

    click.echo("\nRetrieving temporary bucket ID")
    temp_bucket_id = create_temp_bucket(session)

    # If any exception happens now, we want to make sure we delete the
    # temporary bucket to prevent a build up in the user's quota
    try:
        # Upload all files
        upload_files(session, temp_bucket_id, files)
        details = upload_metadata(session, definition, temp_bucket_id)
    except BaseException:
        click.echo("Deleting temporary bucket")
        delete_temp_bucket(session, temp_bucket_id)
        raise

    # Output Details
    click.echo("\nUpload successful")
    click.echo(f"Dataset ID: {details['datasetId']}")
    click.echo(f"Version ID: {details['versionId']}")
    click.echo(f"Metadata ID: {details['metadataId']}")


def upload_files(
    session: DAFNISession, temp_bucket_id: str, files: List[click.Path]
):
    """Function to upload all given files to a temporary bucket via the Minio
    API

    Args:
        session (DAFNISession): User session
        temp_bucket_id (str): Minio temporary bucket ID to upload files to
        files (List[click.Path]): List of Paths to dataset data files
    """
    click.echo("Retrieving file upload URls")
    file_names = {basename(normpath(file_path)): file_path for file_path in files}
    upload_urls = get_data_upload_urls(session, temp_bucket_id, list(file_names.keys()))

    click.echo("Uploading files")
    for key, value in upload_urls["URLs"].items():
        upload_file_to_minio(session, value, file_names[key])


def upload_metadata(
    session: DAFNISession, definition: click.Path, temp_bucket_id: str
) -> dict:
    """Function to upload the Metadata to the Minio API, with the
    given Minio Temporary Upload ID

    Deletes the temporary upload bucket if unsuccessful to avoid
    any unnecessary build up

    Args:
        session ([type]): User session
        definition (click.Path): Path to Metadata file
        temp_bucket_id (str): Minio Temporary Bucket ID

    Returns:
        dict: Upload response in json format
    """
    click.echo("Uploading Metadata File")
    with open(definition, "r", encoding="utf-8") as definition_file:
        try:
            response = upload_dataset_metadata(
                session, temp_bucket_id, json.load(definition_file)
            )
        except (EndpointNotFoundError, DAFNIError, HTTPError) as err:
            click.echo(f"\nMetadata upload failed: {err}")

            raise SystemExit(1) from err

    return response
