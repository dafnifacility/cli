import importlib.resources
import json
from pathlib import Path
from typing import Optional

import click

from dafni_cli.datasets.dataset_upload import (
    modify_dataset_metadata_for_upload,
)


###############################################################################
# COMMAND: Create an ENTITY to upload to DAFNI
###############################################################################
@click.group(help="Create an entity for upload to DAFNI")
def create():
    """Creates entities e.g. dataset-metadata for upload to DAFNI"""


###############################################################################
# COMMAND: Create a DATASET's metadata ready for upload to DAFNI
###############################################################################
@create.command(help="Create a dataset metadata file ready for upload to DAFNI")
@click.argument(
    "save_path", required=True, type=click.Path(exists=False, path_type=Path)
)
@click.option(
    "--version-message",
    type=str,
    default=None,
    help="Version message to replace in any existing or provided metadata.",
)
def dataset_metadata(
    save_path: Path,
    version_message: Optional[str],
):
    """Creates a new file containing a new Dataset's metadata ready for upload
    to DAFNI

    Args:
        save_path (Path): Path to save the metadata file to
        version_message (Optional[str]): Version message
        save (Optional[Path]): Path to save existing metadata in for editing
    """

    # Load template dataset metadata
    template_metadata = json.loads(
        importlib.resources.read_text(
            "dafni_cli.data", "dataset_metadata_template.json"
        )
    )

    # Load/modify the existing metadata according to the user input
    dataset_metadata_dict = modify_dataset_metadata_for_upload(
        existing_metadata=template_metadata,
        metadata_path=None,
        version_message=version_message,
    )

    with open(save_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(dataset_metadata_dict, indent=4, sort_keys=True))

    click.echo(f"Saved dataset metadata to {save_path}")
