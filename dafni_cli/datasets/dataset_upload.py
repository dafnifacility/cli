import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import click
from requests.exceptions import HTTPError

import dafni_cli.api.datasets_api as datasets_api
from dafni_cli.api.exceptions import DAFNIError, EndpointNotFoundError
from dafni_cli.api.minio_api import (
    create_temp_bucket,
    delete_temp_bucket,
    get_data_upload_urls,
    upload_file_to_minio,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.datasets.dataset_metadata import (
    DATASET_METADATA_SUBJECTS,
    DATASET_METADATA_THEMES,
    DATASET_METADATA_UPDATE_FREQUENCIES,
)

# Keys inside dataset metadata returned from the API that are invalid for
# uploading
METADATA_KEYS_INVALID_FOR_UPLOAD = [
    "@id",
    "dct:issued",
    "dct:modified",
    "mediatypes",
    "version_history",
    "auth",
    "dcat:distribution",
]


def remove_dataset_metadata_invalid_for_upload(metadata: dict):
    """Function to remove metadata for a dataset that is given when getting it
    but are not valid during upload

    Args:
        metadata (dict): The metadata to modify
    """

    for key in METADATA_KEYS_INVALID_FOR_UPLOAD:
        if key in metadata:
            del metadata[key]


def modify_dataset_metadata_for_upload(
    existing_metadata: dict,
    metadata_path: Optional[Path] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    identifiers: Optional[Tuple[str]] = None,
    subject: Optional[str] = None,
    themes: Optional[Tuple[str]] = None,
    language: Optional[str] = None,
    keywords: Optional[Tuple[str]] = None,
    standard: Optional[Tuple[str, str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    organisation: Optional[Tuple[str, str]] = None,
    people: Optional[Tuple[Tuple[str, str]]] = None,
    created_date: Optional[datetime] = None,
    update_frequency: Optional[str] = None,
    publisher: Optional[Tuple[str, str]] = None,
    contact_point: Optional[Tuple[str]] = None,
    license: Optional[str] = None,
    rights: Optional[str] = None,
    version_message: Optional[str] = None,
) -> dict:
    """Modifies existing dataset metadata or that loaded from a file according
    to user specified parameters and in a format ready for upload

    Args:
        existing_metadata (dict): Dictionary of existing metadata from the API
        metadata_path (Optional[Path]): Path to a Dataset metadata file.
                        When None will use the existing_metadata instead

        The following parameters are metadata properties that when specified
        will replace what already exists in the given/loaded metadata.

        title (Optional[str]): Dataset title
        description (Optional[str]): Dataset description
        identifiers (Optional[Tuple[str]]): Dataset identifiers
        subject (Optional[str]): Dataset subject (One of
                                 DATASET_METADATA_SUBJECTS)
        themes (Optional[Tuple[str]]): Dataset themes (One of
                                 DATASET_METADATA_THEMES)
        language (Optional[str]): Dataset language e.g. en
        keywords (Optional[Tuple[str]]): Dataset keywords used for data
                                         searches
        standard (Optional[Tuple[str, str]]): Dataset standard consisting of
                                a name and URL
        start_date (Optional[datetime]): Dataset start date
        end_date (Optional[datetime]): Dataset end date
        organisation (Optional[Tuple[str, str]]): Name and URL of the
                                organisation that created the dataset
        person (Optional[Tuple[Tuple[str, str]]]): Name and ID of a person
                                involved in the creation of the dataset
        created_date (Optional[datetime]): Dataset creation date
        update_frequency (Optional[str]): Dataset update frequency, one of
                                DATASET_METADATA_UPDATE_FREQUENCIES
        publisher (Optional[Tuple[str, str]]): Dataset publisher name and ID
        contact_point (Optional[Tuple[str, str]]): Dataset contact point name
                                and email address
        license (Optional[str]): URL to a license that applies to the dataset
        rights (Optional[str]): Description of any usage rights, restrictions
                                or citations required by users of the dataset
        version_message (Optional[str]): Version message
    Returns:
        dict: The modified dataset metadata

    Raises:
        ValueError: If a value is found to be invalid
    """

    # Load the metadata from a file if present, or otherwise use the existing
    if metadata_path:
        with open(metadata_path, "r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
    else:
        metadata = deepcopy(existing_metadata)

    remove_dataset_metadata_invalid_for_upload(metadata)

    # Make modifications to the metadata from the inputs
    if title:
        metadata["dct:title"] = title
    if description:
        metadata["dct:description"] = description
    if identifiers:
        metadata["dct:identifier"] = list(identifiers)
    if subject:
        if subject not in DATASET_METADATA_SUBJECTS:
            raise ValueError(
                f"Subject '{subject}' is invalid, choose one from {''.join(DATASET_METADATA_SUBJECTS)}"
            )

        metadata["dct:subject"] = subject
    if themes:
        for theme in themes:
            if theme not in DATASET_METADATA_THEMES:
                raise ValueError(
                    f"Theme '{theme}' is invalid, choose one from {''.join(DATASET_METADATA_THEMES)}"
                )
        metadata["dcat:theme"] = list(themes)
    if language:
        metadata["dct:language"] = language
    if keywords:
        metadata["dcat:keyword"] = list(keywords)
    if standard:
        metadata["dct:conformsTo"]["label"] = standard[0]
        metadata["dct:conformsTo"]["@id"] = standard[1]
    if start_date:
        metadata["dct:PeriodOfTime"]["time:hasBeginning"] = start_date.isoformat()
    if end_date:
        metadata["dct:PeriodOfTime"]["time:hasEnd"] = end_date.isoformat()
    if organisation:
        metadata["dct:creator"].append(
            {
                "@type": "foaf:Organization",
                "foaf:name": organisation[0],
                "@id": organisation[1],
                "internalID": None,
            }
        )
    if people:
        for person in people:
            metadata["dct:creator"].append(
                {
                    "@type": "foaf:Person",
                    "foaf:name": person[0],
                    "@id": person[1],
                    "internalID": None,
                }
            )
    if created_date:
        metadata["dct:created"] = created_date.isoformat()
    if update_frequency:
        if update_frequency not in DATASET_METADATA_UPDATE_FREQUENCIES:
            raise ValueError(
                f"Update frequency '{update_frequency}' is invalid, choose one from {''.join(DATASET_METADATA_UPDATE_FREQUENCIES)}"
            )
        metadata["dct:accrualPeriodicity"] = update_frequency
    if publisher:
        metadata["dct:publisher"]["foaf:name"] = publisher[0]
        metadata["dct:publisher"]["@id"] = publisher[1]
    if contact_point:
        metadata["dcat:contactPoint"]["vcard:fn"] = contact_point[0]
        metadata["dcat:contactPoint"]["vcard:hasEmail"] = contact_point[1]
    if license:
        metadata["dct:license"]["@id"] = license
    if rights:
        metadata["dct:rights"] = rights
    if version_message:
        metadata["dafni_version_note"] = version_message

    return metadata


def upload_files(session: DAFNISession, temp_bucket_id: str, file_paths: List[Path]):
    """Function to upload all given files to a temporary bucket via the Minio
    API

    Args:
        session (DAFNISession): User session
        temp_bucket_id (str): Minio temporary bucket ID to upload files to
        file_paths (List[Path]): List of Paths to dataset data files
    """
    click.echo("Retrieving file upload URls")
    file_names = {file_path.name: file_path for file_path in file_paths}
    upload_urls = get_data_upload_urls(session, temp_bucket_id, list(file_names.keys()))

    click.echo("Uploading files")
    for key, value in upload_urls["URLs"].items():
        upload_file_to_minio(session, value, file_names[key])


def _commit_metadata(
    session: DAFNISession,
    metadata: dict,
    temp_bucket_id: str,
    dataset_id: Optional[str] = None,
) -> dict:
    """Function to upload the metadata to the NID API and
    commit the dataset

    Deletes the temporary upload bucket if unsuccessful to avoid
    any unnecessary build up

    Args:
        session ([type]): User session
        metadata (dict): The metadata to upload
        temp_bucket_id (str): Minio Temporary Bucket ID
        dataset_id (str): ID of an existing dataset to upload the metadata to

    Returns:
        dict: Upload response in json format
    """
    click.echo("Uploading metadata file")
    try:
        response = datasets_api.upload_dataset_metadata(
            session, temp_bucket_id, metadata, dataset_id=dataset_id
        )
    except (EndpointNotFoundError, DAFNIError, HTTPError) as err:
        click.echo(f"\nMetadata upload failed: {err}")

        raise SystemExit(1) from err

    return response


def upload_dataset(
    session: DAFNISession,
    metadata: dict,
    file_paths: List[Path],
    dataset_id: Optional[str] = None,
) -> None:
    """Function to upload a Dataset

    Args:
        session (DAFNISession): User session
        metadata (dict): Metadata to upload
        file_paths (List[Path]): List of Paths to dataset data files
        dataset_id (Optional[str]): ID of an existing dataset to add a version
                                    to. Creates a new dataset if None.
    """

    click.echo("\nRetrieving temporary bucket ID")
    temp_bucket_id = create_temp_bucket(session)

    # If any exception happens now, we want to make sure we delete the
    # temporary bucket to prevent a build up in the user's quota
    try:
        # Upload all files
        upload_files(session, temp_bucket_id, file_paths)
        details = _commit_metadata(
            session, metadata, temp_bucket_id, dataset_id=dataset_id
        )
    except BaseException:
        click.echo("Deleting temporary bucket")
        delete_temp_bucket(session, temp_bucket_id)
        raise

    # Output Details
    click.echo("\nUpload successful")
    click.echo(f"Dataset ID: {details['datasetId']}")
    click.echo(f"Version ID: {details['versionId']}")
    click.echo(f"Metadata ID: {details['metadataId']}")


def upload_dataset_metadata_version(
    session: DAFNISession,
    dataset_id: str,
    version_id: str,
    metadata: dict,
) -> None:
    """Function to upload a new metadata version to an existing dataset

    Args:
        session (DAFNISession): User session
        dataset_id (str): ID of an existing dataset to add the new metadata
                          version to
        version_id (str): Version ID fo an existing dataset to add the new
                          metadata version to
        metadata (dict): Metadata to upload

    """

    details = datasets_api.upload_dataset_metadata_version(
        session, dataset_id=dataset_id, version_id=version_id, metadata=metadata
    )

    # Output Details
    click.echo("\nUpload successful")
    click.echo(f"Dataset ID: {details['datasetId']}")
    click.echo(f"Version ID: {details['versionId']}")
    click.echo(f"Metadata ID: {details['metadataId']}")
