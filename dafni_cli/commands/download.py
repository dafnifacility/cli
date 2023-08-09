from pathlib import Path
from typing import List, Optional

import click
from click import Context

from dafni_cli.api.session import DAFNISession
from dafni_cli.commands.helpers import (
    cli_get_latest_dataset_metadata,
    cli_select_dataset_files,
)
from dafni_cli.commands.options import click_optional_tuple_none_callback
from dafni_cli.datasets.dataset_download import download_dataset
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata


@click.group(help="Download entity from DAFNI")
@click.pass_context
def download(ctx: Context):
    """Download entity from DAFNI.

    Args:
        ctx (Context): Context containing the user session.
    """
    ctx.ensure_object(dict)
    ctx.obj["session"] = DAFNISession()


@download.command(help="Download all dataset files for a given version")
@click.option(
    "--directory",
    type=click.Path(exists=True, dir_okay=True, path_type=Path),
    help="Directory to save the zipped Dataset files to. Default is the current working directory",
)
@click.argument("version-id", nargs=1, required=True, type=str)
@click.argument(
    "files",
    nargs=-1,
    required=False,
    type=str,
    callback=click_optional_tuple_none_callback,
)
@click.pass_context
def dataset(
    ctx: Context,
    version_id: List[str],
    directory: Optional[Path],
    files: Optional[List[str]],
):
    """Download all files associated with the given Dataset Version.

    Args:
        ctx (Context): CLI context
        version_id (str): Dataset version ID
        directory (Optional[Path]): Directory to download files to (when None
                                    will use the current working directory)
        files (Optional[List[str]]): List of specific files to download (allows
                                     glob-like wildcards)
    """
    metadata = parse_dataset_metadata(
        cli_get_latest_dataset_metadata(ctx.obj["session"], version_id)
    )

    if len(metadata.files) > 0:
        selected_files = cli_select_dataset_files(metadata, files=files)
        if len(selected_files) > 0:
            download_dataset(ctx.obj["session"], selected_files, directory)
        else:
            click.echo("No files selected to download")
    else:
        click.echo(
            "There are no files currently associated with the Dataset to download"
        )
