from os.path import normpath, basename
from typing import List
import click
import json
from requests.exceptions import HTTPError

from dafni_cli.api.datasets_api import (
    get_dataset_upload_urls,
    get_dataset_upload_id,
    upload_dataset_metadata,
)
from dafni_cli.api.minio_api import upload_file_to_minio


def upload_new_dataset_files(jwt, definition: click.Path, files: List[click.Path]):
    click.echo("\nRetrieving Temporary Upload ID")
    upload_id = get_dataset_upload_id(jwt)

    click.echo("Retrieveing File Upload URls")
    file_names = {basename(normpath(file_path)): file_path for file_path in files}
    upload_urls = get_dataset_upload_urls(jwt, upload_id, list(file_names.keys()))

    click.echo("Uploading Dataset Files")
    for key, value in upload_urls["URLs"].items():
        upload_file_to_minio(jwt, value, file_names[key])

    click.echo("Uploading Dataset Metadata")
    with open(definition, "r") as definition_file:
        try:
            response = upload_dataset_metadata(
                jwt, upload_id, json.load(definition_file)
            )
        except HTTPError:
            click.echo("\nMetadata Upload Failed")
            click.echo(
                "See https://github.com/dafnifacility/metadata-schema for more details"
            )
            exit(1)

    return response