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


def upload_model(
    session: DAFNISession,
    definition_path: Path,
    image_path: Path,
    version_message: str,
    parent_id: Optional[str] = None,
):
    click.echo("Validating model definition")
    try:
        validate_model_definition(session, definition_path)
    except ValidationError as err:
        click.echo(err)

        raise SystemExit(1) from err

    click.echo("Getting urls")
    upload_id, urls = get_model_upload_urls(session)
    definition_url = urls["definition"]
    image_url = urls["image"]

    click.echo("Uploading model definition and image")
    upload_file_to_minio(session, definition_url, definition_path)
    upload_file_to_minio(session, image_url, image_path)

    click.echo("Ingesting model")
    model_version_ingest(session, upload_id, version_message, parent_id)

    click.echo("Model upload complete")
