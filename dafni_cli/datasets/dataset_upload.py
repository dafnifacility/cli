from os.path import normpath, basename
from typing import List
import json
import click
from requests.exceptions import HTTPError

from dafni_cli.utils import prose_print
from dafni_cli.consts import CONSOLE_WIDTH
from dafni_cli.api.minio_api import (
    get_data_upload_urls,
    get_data_upload_id,
    upload_file_to_minio,
    upload_dataset_metadata,
)


def upload_new_dataset_files(
    jwt, definition: click.Path, files: List[click.Path]
) -> None:
    """Function to upload all files associated with a new Dataset

    Args:
        jwt ([type]): Users JWT
        definition (click.Path): Path to Dataset metadata file
        files (List[click.Path]): List of Paths to dataset data files
    """
    # Upload all files
    upload_id = upload_files(jwt, files)
    details = upload_metadata(jwt, definition, upload_id)

    # Output Details
    click.echo("\nUpload Successful")
    click.echo(f"Dataset ID: {details['datasetId']}")
    click.echo(f"Version ID: {details['versionId']}")
    click.echo(f"Metadata ID: {details['metadataId']}")


def upload_files(jwt, files: List[click.Path]) -> str:
    """Function to get a temporary Upload ID, and upload all given
    files to the Minio API

    Args:
        jwt ([type]): Users JWT
        files (List[click.Path]): List of Paths to dataset data files

    Returns:
        str: Minio Temporary Upload ID
    """
    click.echo("\nRetrieving Temporary Upload ID")
    upload_id = get_data_upload_id(jwt)

    click.echo("Retrieving File Upload URls")
    file_names = {basename(normpath(file_path)): file_path for file_path in files}
    upload_urls = get_data_upload_urls(jwt, upload_id, list(file_names.keys()))

    click.echo("Uploading Files")
    for key, value in upload_urls["URLs"].items():
        upload_file_to_minio(jwt, value, file_names[key])

    return upload_id


def upload_metadata(jwt, definition: click.Path, upload_id: str) -> dict:
    """Function to upload the Metadata to the Minio API, with the
    given Minio Temporary Upload ID

    Args:
        jwt ([type]): Users JWT
        definition (click.Path): Path to Metadata file
        upload_id (str): Minio Temporary Upload ID

    Returns:
        dict: Upload response in json format
    """
    click.echo("Uploading Metadata File")
    with open(definition, "r") as definition_file:
        try:
            response = upload_dataset_metadata(
                jwt, upload_id, json.load(definition_file)
            )
            response.raise_for_status()
        except HTTPError as e:
            click.echo("\nMetadata Upload Failed")
            prose_print("\n".join(response.json()), CONSOLE_WIDTH)
            raise SystemExit(1) from e

    return response.json()
