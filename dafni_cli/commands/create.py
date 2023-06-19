import importlib.resources
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import click

from dafni_cli.commands.options import dataset_metadata_common_options
from dafni_cli.datasets.dataset_upload import modify_dataset_metadata_for_upload


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
@dataset_metadata_common_options(all_optional=False)
def dataset_metadata(
    save_path: Path,
    title: str,
    description: str,
    identifier: Optional[Tuple[str]],
    subject: str,
    theme: Optional[Tuple[str]],
    language: str,
    keyword: Tuple[str],
    standard: Optional[Tuple[str, str]],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    organisation: Tuple[str, str],
    person: Optional[Tuple[Tuple[str, str]]],
    created_date: Optional[datetime],
    update_frequency: Optional[str],
    publisher: Optional[Tuple[str, str]],
    contact: Tuple[str, str],
    license: str,
    rights: Optional[str],
    version_message: str,
):
    """Creates a new file containing a new Dataset's metadata ready for upload
    to DAFNI

    Args:
        save_path (Path): Path to save the metadata file to

        For the rest see dataset_metadata_common_options in options.py
    """

    # Load template dataset metadata
    template_metadata = json.loads(
        importlib.resources.files("dafni_cli.data")
        .joinpath("dataset_metadata_template.json")
        .read_text(encoding="utf-8")
    )

    # Load/modify the existing metadata according to the user input
    dataset_metadata_dict = modify_dataset_metadata_for_upload(
        existing_metadata=template_metadata,
        title=title,
        description=description,
        subject=subject,
        identifiers=identifier,
        themes=theme,
        language=language,
        keywords=keyword,
        standard=standard,
        start_date=start_date,
        end_date=end_date,
        organisation=organisation,
        people=person,
        created_date=created_date,
        update_frequency=update_frequency,
        publisher=publisher,
        contact=contact,
        license=license,
        rights=rights,
        version_message=version_message,
    )

    with open(save_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(dataset_metadata_dict, indent=4, sort_keys=True))

    click.echo(f"Saved dataset metadata to {save_path}")
