from pathlib import Path
import pathlib
from typing import List, Optional

import click
from click import Context

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.session import DAFNISession
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.utils import write_files_to_zip


@click.group(help="Download entity from DAFNI")
@click.pass_context
def download(ctx: Context):
    """Download entity from DAFNI.

    Args:
        ctx (Context): Context containing the user session.
    """
    ctx.ensure_object(dict)
    ctx.obj["session"] = DAFNISession()


@download.command(help="Download all dataset files for given version")
@click.option(
    "--directory",
    type=click.Path(exists=True, dir_okay=True, path_type=Path),
    help="Directory to save the zipped Dataset files to. Default is the current working directory",
)
@click.argument("dataset-id", nargs=1, required=True, type=str)
@click.argument("version-id", nargs=1, required=True, type=str)
@click.pass_context
def dataset(
    ctx: Context,
    dataset_id: str,
    version_id: List[str],
    directory: Optional[Path],
):
    """Download all files associated with the given Dataset Version.

    Args:
        ctx (Context): CLI context
        dataset_id (str): Dataset ID
        version_id (str): Dataset version ID
        directory (Optional[Path]): Directory to write zip folder to
    """
    metadata = parse_dataset_metadata(
        get_latest_dataset_metadata(ctx.obj["session"], dataset_id, version_id)
    )

    if len(metadata.files) > 0:
        # Download all files
        file_names, file_contents = metadata.download_dataset_files(ctx.obj["session"])

        # Setup file paths
        if not directory:
            directory = Path.cwd()
        zip_name = f"Dataset_{dataset_id}_{version_id}.zip"
        path = directory / zip_name
        # Write files to disk
        write_files_to_zip(path, file_names, file_contents)
        # Output file details
        click.echo("\nThe dataset files have been downloaded to:")
        click.echo(path)
        metadata.output_datafiles_table()
    else:
        click.echo(
            "\nThere are no files currently associated with the Dataset to download"
        )
