import importlib.resources
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import click

from dafni_cli.consts import DATE_INPUT_FORMAT, DATE_INPUT_FORMAT_VERBOSE
from dafni_cli.datasets.dataset_metadata import (
    DATASET_METADATA_SUBJECTS,
    DATASET_METADATA_THEMES,
    DATASET_METADATA_UPDATE_FREQUENCIES,
)
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
@click.option(
    "--title",
    type=str,
    required=True,
    help="Title of the dataset",
)
@click.option(
    "--description",
    type=str,
    required=True,
    help="Description of the dataset",
)
@click.option(
    "--identifier",
    type=str,
    default=None,
    multiple=True,
    help="Permanent URL of external identifier for this dataset (e.g. DOI). (Can have multiple)",
)
@click.option(
    "--subject",
    type=click.Choice(DATASET_METADATA_SUBJECTS),
    required=True,
    help="Subject, one of those found at https://inspire.ec.europa.eu/metadata-codelist/TopicCategory",
)
@click.option(
    "--theme",
    type=click.Choice(DATASET_METADATA_THEMES),
    default=None,
    multiple=True,
    help="Theme, one of those found at https://inspire.ec.europa.eu/Themes/Data-Specifications/2892. Can have multiple.",
)
@click.option(
    "--language",
    type=str,
    required=True,
    help="Language",
)
@click.option(
    "--keyword",
    type=str,
    required=True,
    multiple=True,
    help="Keyword used in data searches (Can have multiple)",
)
@click.option(
    "--standard",
    type=(str, str),
    default=None,
    required=False,
    help="Name and URL of a standard to which this dataset conforms (e.g. www.iso.org/standard/39229.html).",
)
@click.option(
    "--start-date",
    default=None,
    help=f"Start date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
)
@click.option(
    "--end-date",
    default=None,
    help=f"End date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
)
@click.option(
    "--organisation",
    type=(str, str),
    required=True,
    help="Name and ID of the organisation that created the dataset. he ID can be an ORCID id or similar.",
)
@click.option(
    "--person",
    type=(str, str),
    multiple=True,
    help="Name and ID of a person who created the dataset. The ID can be an ORCID id or similar. (Can have multiple)",
)
@click.option(
    "--created-date",
    default=datetime.now(),
    help=f"Created date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
)
@click.option(
    "--update-frequency",
    type=click.Choice(DATASET_METADATA_UPDATE_FREQUENCIES),
    default=None,
    help="Update frequency.",
)
@click.option(
    "--publisher",
    type=(str, str),
    default=None,
    help="Publishing organisation name and ID. The ID can be an ORCID id or similar.",
)
@click.option(
    "--contact",
    type=(str, str),
    required=True,
    help="Name and email address of the point of contact for queries about the dataset.",
)
@click.option(
    "--license",
    type=str,
    default="https://creativecommons.org/licences/by/4.0/",
    help="Permanent URL of an applicable license.",
)
@click.option(
    "--rights",
    type=str,
    default=None,
    help="Details of any usage rights, restrictions or citations required by users of the dataset.",
)
@click.option(
    "--version-message",
    type=str,
    required=True,
    default=None,
    help="Version message to replace in any existing or provided metadata.",
)
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
        title (str): Dataset title
        description (str): Dataset description
        identifier (Optional[Tuple[str]]): Dataset identifiers
        subject (str): Dataset subject (One of DATASET_METADATA_SUBJECTS)
        theme (Optional[Tuple[str]]): Dataset themes (One of
                                      DATASET_METADATA_THEMES)
        language (str): Dataset language e.g. en
        keywords (Tuple[str]): Dataset keywords used for data searches
        standard (Optional[Tuple[str, str]]): Dataset standard consisting of
                                a name and URL
        start_date (Optional[datetime]): Dataset start date
        end_date (Optional[datetime]): Dataset end date
        organisation (Tuple[str, str]): Name and URL of the organisation that
                                created the dataset
        person (Optional[Tuple[Tuple[str, str]]]): Name and ID of a person
                                involved in the creation of the dataset
        created_date (Optional[datetime]): Dataset creation date
        update_frequency (Optional[str]): Dataset update frequency, one of
                                DATASET_METADATA_UPDATE_FREQUENCIES
        publisher (Optional[Tuple[str, str]]): Dataset publisher name and ID
        contact (Optional[Tuple[str, str]]): Dataset contact point name
                                and email address
        license (str): URL to a license that applies to the dataset
        rights (Optional[str]): Description of any usage rights, restrictions
                                or citations required by users of the dataset
        version_message (str): Version message
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
