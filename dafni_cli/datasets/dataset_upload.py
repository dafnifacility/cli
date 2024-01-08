import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
from requests.exceptions import HTTPError

import dafni_cli.api.datasets_api as datasets_api
from dafni_cli.api.exceptions import DAFNIError, EndpointNotFoundError, ValidationError
from dafni_cli.api.minio_api import (
    create_temp_bucket,
    delete_temp_bucket,
    get_data_upload_urls,
    upload_file_to_minio,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import DATASET_UPLOAD_FILE_RETRY_ATTEMPTS
from dafni_cli.datasets.dataset_metadata import (
    DATASET_METADATA_LANGUAGES,
    DATASET_METADATA_SUBJECTS,
    DATASET_METADATA_THEMES,
    DATASET_METADATA_UPDATE_FREQUENCIES,
)
from dafni_cli.utils import OverallFileProgressBar, optional_echo, print_json

# Keys inside dataset metadata returned from the API that are invalid for
# uploading
METADATA_KEYS_INVALID_FOR_UPLOAD = [
    "@id",
    "dct:issued",
    "dct:modified",
    "mediatypes",
    "dcat:distribution",
    "dataset_type",
]


def parse_file_names_from_paths(
    paths: List[Path],
    expanded_files_dict: Optional[Dict[str, Path]] = None,
    file_name_prefix: Optional[str] = None,
) -> Dict[str, Path]:
    """Obtains all filenames and filepaths to upload given a set of input
    filepaths that may also contain folders to upload

    All filenames from folders should have a unix style '/' regardless of
    platform

    Args:
        paths (Path): List of paths to check for folders
        expanded_files_dict (Optional[Dict[str, Path]]): Existing files found
        file_name_prefix (Optional[str]): Prefix for the filename to add

    Returns:
        dict[str, Path]: Dictionary with keys being specific filenames to upload
                         and the values as the paths to the corresponding files
    """
    # Avoids dangerous default arg
    if expanded_files_dict is None:
        expanded_files_dict = {}

    for path in paths:
        current_file_name_prefix = (
            f"{file_name_prefix}/{path.name}"
            if file_name_prefix is not None
            else path.name
        )

        if path.is_dir():
            # Expand folder
            expanded_files_dict = parse_file_names_from_paths(
                path.glob("*"),
                expanded_files_dict=expanded_files_dict,
                file_name_prefix=current_file_name_prefix,
            )
        else:
            # Append file
            expanded_files_dict[current_file_name_prefix] = path

    return expanded_files_dict


def remove_dataset_metadata_invalid_for_upload(metadata: dict):
    """Function to remove metadata for a dataset that is given when getting it
    but are not valid during upload

    Args:
        metadata (dict): The metadata to modify
    """

    for key in METADATA_KEYS_INVALID_FOR_UPLOAD:
        if key in metadata:
            del metadata[key]


def _remove_existing_creators_from_metadata(creator_list: List, creator_type: str):
    """Removes any existing creators with a given creator type from
    a list from dataset metadata

    Args:
        creator_list: List of creators
    """
    for creator in creator_list.copy():
        if creator["@type"] == creator_type:
            creator_list.remove(creator)


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
    contact: Optional[Tuple[str]] = None,
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
        language (Optional[str]): Dataset language, one of
                                  DATASET_METADATA_LANGUAGES
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
        contact (Optional[Tuple[str, str]]): Dataset contact point name
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
        metadata = deepcopy(existing_metadata["metadata"])

    remove_dataset_metadata_invalid_for_upload(metadata)

    # Make modifications to the metadata from the inputs
    if title is not None:
        metadata["dct:title"] = title
    if description is not None:
        metadata["dct:description"] = description
    if identifiers is not None:
        metadata["dct:identifier"] = list(identifiers)
    if subject is not None:
        if subject not in DATASET_METADATA_SUBJECTS:
            raise ValueError(
                f"Subject '{subject}' is invalid, choose one from {''.join(DATASET_METADATA_SUBJECTS)}"
            )

        metadata["dct:subject"] = subject
    if themes is not None:
        for theme in themes:
            if theme not in DATASET_METADATA_THEMES:
                raise ValueError(
                    f"Theme '{theme}' is invalid, choose one from {''.join(DATASET_METADATA_THEMES)}"
                )
        metadata["dcat:theme"] = list(themes)
    if language is not None:
        if language not in DATASET_METADATA_LANGUAGES:
            raise ValueError(
                f"Language '{language}' is invalid, choose one from {''.join(DATASET_METADATA_LANGUAGES)}"
            )
        metadata["dct:language"] = language
    if keywords is not None:
        metadata["dcat:keyword"] = list(keywords)
    if standard is not None:
        metadata["dct:conformsTo"]["label"] = standard[0]
        metadata["dct:conformsTo"]["@id"] = standard[1]
    if start_date is not None:
        metadata["dct:PeriodOfTime"]["time:hasBeginning"] = start_date.isoformat()
    if end_date is not None:
        metadata["dct:PeriodOfTime"]["time:hasEnd"] = end_date.isoformat()

    if organisation is not None:
        # Remove any existing
        _remove_existing_creators_from_metadata(
            metadata["dct:creator"], "foaf:Organization"
        )
        metadata["dct:creator"].append(
            {
                "@type": "foaf:Organization",
                "foaf:name": organisation[0],
                "@id": organisation[1],
                "internalID": None,
            }
        )
    if people is not None:
        # Remove any existing
        _remove_existing_creators_from_metadata(metadata["dct:creator"], "foaf:Person")
        for person in people:
            metadata["dct:creator"].append(
                {
                    "@type": "foaf:Person",
                    "foaf:name": person[0],
                    "@id": person[1],
                    "internalID": None,
                }
            )
    if created_date is not None:
        metadata["dct:created"] = created_date.isoformat()
    if update_frequency is not None:
        if update_frequency not in DATASET_METADATA_UPDATE_FREQUENCIES:
            raise ValueError(
                f"Update frequency '{update_frequency}' is invalid, choose one from {''.join(DATASET_METADATA_UPDATE_FREQUENCIES)}"
            )
        metadata["dct:accrualPeriodicity"] = update_frequency
    if publisher is not None:
        metadata["dct:publisher"]["foaf:name"] = publisher[0]
        metadata["dct:publisher"]["@id"] = publisher[1]
    if contact is not None:
        metadata["dcat:contactPoint"]["vcard:fn"] = contact[0]
        metadata["dcat:contactPoint"]["vcard:hasEmail"] = contact[1]
    if license is not None:
        metadata["dct:license"]["@id"] = license
    if rights is not None:
        metadata["dct:rights"] = rights
    if version_message is not None:
        metadata["dafni_version_note"] = version_message

    return metadata


def upload_files(
    session: DAFNISession,
    temp_bucket_id: str,
    paths: List[Path],
    json: bool = False,
):
    """Function to upload all given files to a temporary bucket via the Minio
    API

    If any of the paths are folders they will be expanded according to
    parse_file_names_from_paths such that their new file names will include
    the directory structure as well

    Args:
        session (DAFNISession): User session
        temp_bucket_id (str): Minio temporary bucket ID to upload files to
        paths (List[Path]): List of paths to dataset data files/folders
        json (bool): Whether to print the raw json returned by the DAFNI API

    Raises:
        RuntimeError: If unable to upload the file for some reason
    """
    file_names_and_paths = parse_file_names_from_paths(paths=paths)

    optional_echo("Uploading files", json)

    # For an indication of the overall upload progress
    total_file_size = sum(file_path.stat().st_size for file_path in paths)

    # Progress bar keeping track of all files being uploaded
    with OverallFileProgressBar(
        len(file_names_and_paths), total_file_size
    ) as overall_progress_bar:
        # Obtain upload URLs for each batch separately and wait until uploaded
        # all the files in the current batch before starting the next
        for file_name, file_path in file_names_and_paths.items():
            upload_attempts = 0

            # Try and upload, but if fails for any reason - retry with a new upload URL
            while upload_attempts < DATASET_UPLOAD_FILE_RETRY_ATTEMPTS:
                upload_url = get_data_upload_urls(session, temp_bucket_id, [file_name])[
                    "urls"
                ][file_name]

                try:
                    upload_file_to_minio(
                        session,
                        upload_url,
                        file_path,
                        file_name=file_name,
                        progress_bar=not json,
                    )
                    break
                except RuntimeError as err:
                    upload_attempts += 1

                    if upload_attempts == DATASET_UPLOAD_FILE_RETRY_ATTEMPTS:
                        # Completely broken
                        raise RuntimeError(
                            f"Attempted to upload file {DATASET_UPLOAD_FILE_RETRY_ATTEMPTS} times but failed repeatedly"
                        ) from err

            # Completed a file download, update the overall status to reflect
            overall_progress_bar.update(file_names_and_paths[file_name].stat().st_size)


def _commit_metadata(
    session: DAFNISession,
    metadata: dict,
    temp_bucket_id: str,
    dataset_id: Optional[str] = None,
    json: bool = False,
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
        json (bool): Whether to print the raw json returned by the DAFNI API

    Returns:
        dict: Upload response in json format
    """
    optional_echo("Uploading metadata file", json)
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
    paths: List[Path],
    dataset_id: Optional[str] = None,
    json: bool = False,
) -> None:
    """Function to upload a Dataset

    If any of the paths are folders they will be expanded according to
    parse_file_names_from_paths such that their new file names will include
    the directory structure as well

    Args:
        session (DAFNISession): User session
        metadata (dict): Metadata to upload
        paths (List[Path]): List of Paths to dataset data files/folders
        dataset_id (Optional[str]): ID of an existing dataset to add a version
                                    to. Creates a new dataset if None.
        json (bool): Whether to print the raw json returned by the DAFNI API
    """
    optional_echo("Validating metadata", json)
    try:
        datasets_api.validate_metadata(session, metadata)
    except ValidationError as err:
        click.echo(err)
        raise SystemExit(1) from err
    optional_echo("Metadata validation successful", json)

    optional_echo("\nRetrieving temporary bucket ID", json)
    temp_bucket_id = create_temp_bucket(session)

    # If any exception happens now, we want to make sure we delete the
    # temporary bucket to prevent a build up in the user's quota
    try:
        # Upload all files
        upload_files(session, temp_bucket_id, paths, json=json)
        details = _commit_metadata(
            session, metadata, temp_bucket_id, dataset_id=dataset_id, json=json
        )
    except BaseException:
        optional_echo("Deleting temporary bucket", json)
        delete_temp_bucket(session, temp_bucket_id)
        raise

    # Output details
    if json:
        print_json(details)
    else:
        click.echo("\nUpload successful")
        click.echo(f"Dataset ID: {details['datasetId']}")
        click.echo(f"Version ID: {details['versionId']}")
        click.echo(f"Metadata ID: {details['metadataId']}")


def upload_dataset_metadata_version(
    session: DAFNISession,
    dataset_id: str,
    version_id: str,
    metadata: dict,
    json: bool = False,
) -> None:
    """Function to upload a new metadata version to an existing dataset

    Args:
        session (DAFNISession): User session
        dataset_id (str): ID of an existing dataset to add the new metadata
                          version to
        version_id (str): Version ID fo an existing dataset to add the new
                          metadata version to
        metadata (dict): Metadata to upload
        json (bool): Whether to print the raw json returned by the DAFNI API
    """

    details = datasets_api.upload_dataset_metadata_version(
        session, dataset_id=dataset_id, version_id=version_id, metadata=metadata
    )

    # Output Details
    if json:
        print_json(details)
    else:
        click.echo("\nUpload successful")
        click.echo(f"Dataset ID: {details['datasetId']}")
        click.echo(f"Version ID: {details['versionId']}")
        click.echo(f"Metadata ID: {details['metadataId']}")
