from pathlib import Path
from typing import List, Optional

import click
from tqdm import tqdm

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

    # For an indication of the overall download progress - need approximate
    # file size for all files
    total_file_data_to_download = 0
    for file in files:
        total_file_data_to_download += file.size

    # Download each file separately (not zipped on backend)
    with tqdm(
        desc="Overall progress",
        total=total_file_data_to_download,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as overall_progress_bar:
        for file in files:
            # Open the save file
            file_save_path = directory / file.name

            # Stream the file
            with minio_get_request(
                session, file.download_url, stream=True
            ) as download_response:
                file_size = int(download_response.headers.get("content-length", 0))
                click.echo(f"Downloading '{file.name}'...")
                with tqdm.wrapattr(
                    open(file_save_path, "wb"),
                    "write",
                    miniters=1,
                    total=file_size,
                ) as save_file:
                    # Save the file while downloading in chunks
                    for chunk in download_response.iter_content(chunk_size=CHUNK_SIZE):
                        save_file.write(chunk)
            overall_progress_bar.update(file.size)
    click.echo(f"Downloaded files to '{directory}'")
