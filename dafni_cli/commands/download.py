import click
from click import Context
from typing import List, Optional
import os

from dafni_cli.datasets.dataset_metadata import DatasetMetadata
from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.utils import write_files_to_zip


@click.group(help="Download entity from DAFNI")
@click.pass_context
def download(ctx: Context):
    """Download entity from DAFNI."""
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


@download.command(help="Download all dataset files for given version")
@click.option(
    "--directory",
    type=click.Path(exists=True, dir_okay=True),
    help="Directory to save the zipped Dataset files to. Default is the current working directory",
)
@click.argument("dataset-id", nargs=1, required=True, type=str)
@click.argument("version-id", nargs=1, required=True, type=str)
@click.pass_context
def dataset(
    ctx: Context,
    dataset_id: str,
    version_id: List[str],
    directory: Optional[click.Path],
):
    """Download all files associated with the given Dataset Version.

    Args:
        ctx (Context): CLI context
        id (str): Dataset ID
        version_id (str): Dataset version ID
    """
    metadata = get_latest_dataset_metadata(ctx.obj["jwt"], dataset_id, version_id)
    dataset_meta = DatasetMetadata(metadata)

    if len(dataset_meta.files) > 0:
        # Download all files
        file_names, file_contents = dataset_meta.download_dataset_files(ctx.obj["jwt"])

        # Setup file paths
        if not directory:
            directory = os.getcwd()
        zip_name = f"Dataset_{dataset_id}_{version_id}.zip"
        path = os.path.join(directory, zip_name)
        # Write files to disk
        write_files_to_zip(path, file_names, file_contents)
        # Output file details
        click.echo("\nThe dataset files have been downloaded to: ")
        click.echo(os.path.join(directory, zip_name))
        dataset_meta.output_datafiles_table()
    else:
        click.echo(
            "\nThere are no files currently associated with the Dataset to download"
        )
