import json
from os.path import basename, normpath
from typing import List

import click
from requests.exceptions import HTTPError

from dafni_cli.api.exceptions import DAFNIError, EndpointNotFoundError
from dafni_cli.api.minio_api import (
    get_data_upload_id,
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
    # Upload all files
    upload_id = upload_files(session, files)
    details = upload_metadata(session, definition, upload_id)

    # Output Details
    click.echo("\nUpload Successful")
    click.echo(f"Dataset ID: {details['datasetId']}")
    click.echo(f"Version ID: {details['versionId']}")
    click.echo(f"Metadata ID: {details['metadataId']}")


def upload_files(session: DAFNISession, files: List[click.Path]) -> str:
    """Function to get a temporary Upload ID, and upload all given
    files to the Minio API

    Args:
        session (DAFNISession): User session
        files (List[click.Path]): List of Paths to dataset data files

    Returns:
        str: Minio Temporary Upload ID
    """
    click.echo("\nRetrieving Temporary Upload ID")
    upload_id = get_data_upload_id(session)
    print(f"Temp Bucket ID: {upload_id}")

    click.echo("Retrieving File Upload URls")
    file_names = {basename(normpath(file_path)): file_path for file_path in files}
    upload_urls = get_data_upload_urls(session, upload_id, list(file_names.keys()))

    click.echo("Uploading Files")
    for key, value in upload_urls["URLs"].items():
        upload_file_to_minio(session, value, file_names[key])

    return upload_id


def upload_metadata(
    session: DAFNISession, definition: click.Path, upload_id: str
) -> dict:
    """Function to upload the Metadata to the Minio API, with the
    given Minio Temporary Upload ID

    Args:
        session ([type]): User session
        definition (click.Path): Path to Metadata file
        upload_id (str): Minio Temporary Upload ID

    Returns:
        dict: Upload response in json format
    """
    click.echo("Uploading Metadata File")
    with open(definition, "r", encoding="utf-8") as definition_file:
        try:
            response = upload_dataset_metadata(
                session, upload_id, json.load(definition_file)
            )
        except (EndpointNotFoundError, DAFNIError, HTTPError) as err:
            click.echo(f"\nMetadata Upload Failed: {err}")
            raise SystemExit(1) from err

    return response
