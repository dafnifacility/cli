from pathlib import Path
from typing import List, Optional

import click
from dafni_cli.api.minio_api import minio_get_request

from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import CHUNK_SIZE
from dafni_cli.datasets.dataset_metadata import DataFile


def download_dataset(
    session: DAFNISession,
    files: List[DataFile],
    directory: Optional[Path],
):
    """Function to download files in a dataset

    Args:
        session (DAFNISession): User session
        files (List[DataFile]): The files to download
        directory (Optional[path]): Directory to download files to (when None
                                    will use the current working directory)
    """
    # Use current working directory by default
    if not directory:
        directory = Path.cwd()

    # Download each file separately (not zipped on backend)
    for file in files:
        # Open the save file
        file_save_path = directory / file.name

        click.echo(f"Downloading file '{file.name}'")

        # Stream the file
        with minio_get_request(
            session, file.download_url, stream=True
        ) as download_response:
            with open(file_save_path, "wb") as save_file:
                # Save the file while downloading in chunks
                for chunk in download_response.iter_content(chunk_size=CHUNK_SIZE):
                    save_file.write(chunk)
            click.echo(f"Downloaded to '{file_save_path}'")
