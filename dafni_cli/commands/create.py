from datetime import datetime
import importlib.resources
import json
from pathlib import Path
from typing import List, Optional, Tuple

import click

from dafni_cli.consts import DATE_INPUT_FORMAT, DATE_INPUT_FORMAT_VERBOSE
from dafni_cli.datasets.dataset_upload import modify_dataset_metadata_for_upload


###############################################################################
# COMMAND: Create an ENTITY to upload to DAFNI
###############################################################################
@click.group(help="Create an entity for upload to DAFNI")
def create():
    """Creates entities e.g. dataset-metadata for upload to DAFNI"""


# TODO: Move somewhere else
DATASET_METADATA_SUBJECTS = [
    "Biota",
    "Boundaries",
    "Climate / Meteorology / Atmosphere",
    "Economy",
    "Elevation",
    "Environment",
    "Farming",
    "Geoscientific Information",
    "Health",
    "Imagery / Base Maps / Earth Cover",
    "Inland Waters",
    "Intelligence / Military",
    "Locations",
    "Ocean",
    "Planning / Cadastre",
    "Society",
    "Structure",
    "Transportation",
    "Utilities / Communication",
]

DATASET_METADATA_THEMES = [
    "Addresses",
    "Administrative units",
    "Agricultural and aquaculture facilities",
    "Area management / restriction / regulation zones & reporting units",
    "Atmospheric conditions",
    "Bio-geographical regions",
    "Buildings",
    "Cadastral parcels",
    "Coordinate reference systems",
    "Elevation",
    "Energy Resources",
    "Environmental monitoring Facilities",
    "Geographical grid systems",
    "Geographical names",
    "Geology",
    "Habitats and biotopes",
    "Human health and safety",
    "Hydrology",
    "Land cover",
    "Land use",
    "Meteorological geographical features",
    "Mineral Resources",
    "Natural risk zones",
    "Oceanographic geographical features",
    "Orthoimagery",
    "Population distribution and demography",
    "Production and industrial facilities",
    "Protected sites",
    "Sea regions",
    "Soil",
    "Species distribution",
    "Statistical units",
    "Transport networks",
    "Utility and governmental services",
]

DATASET_METADATA_UPDATE_FREQUENCIES = [
    "Triennial",
    "Biennial",
    "Annual",
    "Semiannual",
    "Three times a year",
    "Quarterly",
    "Bimonthly",
    "Monthly",
    "Semimonthly",
    "Biweekly",
    "Three times a month",
    "Weekly",
    "Semiweekly",
    "Three times a week",
    "Daily",
    "Continuous",
    "Irregular",
]


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
    "--standard-name",
    type=str,
    default=None,
    required=False,
    help="Name of a standard to which this dataset conforms (e.g. www.iso.org/standard/39229.html).",
)
@click.option(
    "--standard-url",
    type=str,
    default=None,
    required=False,
    help="Permanent URL of a standard to which this dataset conforms (e.g. www.iso.org/standard/39229.html).",
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
    "--organisation-name",
    type=str,
    required=True,
    help="Name of the organisation that created the dataset",
)
@click.option(
    "--organisation-id",
    type=str,
    required=True,
    help="ID of the organisation that created the dataset e.g. ORCID id or similar.",
)
@click.option(
    "--person-name",
    type=str,
    multiple=True,
    help="Name of a person who created the dataset. (Can have multiple)",
)
@click.option(
    "--person-id",
    type=str,
    multiple=True,
    help="ID of a person who created the dataset e.g. ORCID id or similar. (Can have multiple)",
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
    "--publisher-name",
    type=str,
    default=None,
    help="Publishing organisation name.",
)
@click.option(
    "--publisher-id",
    type=str,
    default=None,
    help="Publishing organisation identifier e.g. ORCID id or similar.",
)
@click.option(
    "--contact-point-name",
    type=str,
    required=True,
    help="Name of the point of contact for queries about the dataset.",
)
@click.option(
    "--contact-point-email",
    type=str,
    required=True,
    help="Email address of the point of contact for queries about the dataset.",
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
    identifier: Optional[str],
    subject: str,
    theme: Tuple[str],
    language: str,
    keyword: Tuple[str],
    standard_name: Optional[str],
    standard_url: Optional[str],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    organisation_name: str,
    organisation_id: str,
    person_name: Optional[Tuple[str]],
    person_id: Optional[Tuple[str]],
    created_date: Optional[datetime],
    update_frequency: Optional[str],
    publisher_name: Optional[str],
    publisher_id: Optional[str],
    contact_point_name: str,
    contact_point_email: str,
    license: str,
    rights: Optional[str],
    version_message: str,
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
        title=title,
        description=description,
        subject=subject,
        identifiers=identifier,
        themes=theme,
        language=language,
        keywords=keyword,
        standard_name=standard_name,
        standard_url=standard_url,
        start_date=start_date,
        end_date=end_date,
        organisation_id=organisation_id,
        organisation_name=organisation_name,
        person_name=person_name,
        person_id=person_id,
        created_date=created_date,
        update_frequency=update_frequency,
        publisher_name=publisher_name,
        publisher_id=publisher_id,
        contact_point_name=contact_point_name,
        contact_point_email=contact_point_email,
        license=license,
        rights=rights,
        version_message=version_message,
    )

    with open(save_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(dataset_metadata_dict, indent=4, sort_keys=True))

    click.echo(f"Saved dataset metadata to {save_path}")
