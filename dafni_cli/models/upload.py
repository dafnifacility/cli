from pathlib import Path
from typing import Optional

import click

from dafni_cli.api.exceptions import ValidationError
from dafni_cli.api.minio_api import upload_file_to_minio
from dafni_cli.api.models_api import (
    get_model_upload_urls,
    model_version_ingest,
    validate_model_definition,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.utils import optional_echo, print_json, is_valid_definition_file


def upload_model(
    session: DAFNISession,
    definition_path: Path,
    image_path: Path,
    version_message: str,
    parent_id: Optional[str] = None,
    json: bool = False,
):
    """Uploads a model to DAFNI

    Args:
        session (DAFNISession): User session
        definition_path (Path): Path to the model definition file
        image_path (Path): Path to the image file
        version_message (str): Version message to tag the upload with
        parent_id (Optional[str]): ID of a parent model. If given will upload
                                   a new version of the model, otherwise will
                                   upload a new model.
        json (bool): Whether to print the raw json returned by the DAFNI API
    """

    if not is_valid_definition_file(definition_path) :
        click.echo("Wrong definition file type.")
        raise SystemExit(1)
    
    optional_echo("Validating model definition", json)
    try:
        validate_model_definition(session, definition_path)
    except ValidationError as err:
        click.echo(err)

        raise SystemExit(1) from err

    optional_echo("Getting urls", json)
    upload_id, urls = get_model_upload_urls(session)
    definition_url = urls["definition"]
    image_url = urls["image"]

    optional_echo("Uploading model definition and image", json)
    upload_file_to_minio(session, definition_url, definition_path)
    upload_file_to_minio(session, image_url, image_path)

    optional_echo("Ingesting model", json)
    details = model_version_ingest(session, upload_id, version_message, parent_id)

    # Output details
    if json:
        print_json(details)
    else:
        click.echo("\nUpload successful")
        click.echo(f"Version ID: {details['version_id']}")
