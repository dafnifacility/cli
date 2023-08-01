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
    """Function to download a list of files found within a dataset

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
    total_file_size = sum(file.size for file in files)

    # Download each file separately (not zipped on backend)
    click.echo("Downloading files...")
    click.echo()

    # Gives a string description for the overall status progress bar
    overall_description = (
        lambda file_number: f"Overall progress {file_number}/{len(files)}"
    )

    # Progress bar keeping track of all files being downloaded
    with tqdm(
        desc=overall_description(0),
        miniters=1,
        total=total_file_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as overall_progress_bar:
        # Each file downloaded individually with its own progress bar
        for index, file in enumerate(files):
            file_save_path = directory / file.name

            # Stream the file download
            with minio_get_request(
                session, file.download_url, stream=True
            ) as download_response:
                # Full file size
                file_size = int(download_response.headers.get("content-length", 0))

                # Allow tqdm to handle the progress bar based on the data saved
                with tqdm.wrapattr(
                    open(file_save_path, "wb"),
                    "write",
                    desc=file.name,
                    miniters=1,
                    total=file_size,
                ) as save_file:
                    # Download and save file in chunks
                    for chunk in download_response.iter_content(chunk_size=CHUNK_SIZE):
                        save_file.write(chunk)

            # Completed a file download, update the overall status to reflect
            overall_progress_bar.set_description(overall_description(index + 1))
            overall_progress_bar.update(file.size)

    click.echo()
    click.echo(f"Downloaded files to '{directory}'")
