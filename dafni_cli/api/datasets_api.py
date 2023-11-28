from typing import List, Optional

import requests
from requests import Response

from dafni_cli.api.exceptions import (
    DAFNIError,
    EndpointNotFoundError,
    ResourceNotFoundError,
    ValidationError,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import NID_API_URL, SEARCH_AND_DISCOVERY_API_URL


# Validation function for validating the dataset-metadata
def validate_metadata(session: DAFNISession, metadata: dict):
    """
    Function to validate metadata prior to upload

    Args:
        session (DAFNISession): User session
        metadata: metadata in .json format
    Returns:
        Raises validation error if unsuccessful
    """
    url = f"{NID_API_URL}/nid/validate/"
    metadata = {"metadata": metadata}
    try:
        session.post_request(url=url, json=metadata)
    except DAFNIError as err:
        raise ValidationError(f"Dataset metadata validation failed. {err}")


# TODO this should work with pagination - check
def get_all_datasets(session: DAFNISession, filters: dict) -> List[dict]:
    """Function to retrieve all datasets available to the user

    Args:
        session (DAFNISession): User session
        filters (dict): dict of filters to apply to the get datasets query

    Returns:
        List[dict]: List of available datasets
    """
    url = f"{SEARCH_AND_DISCOVERY_API_URL}/catalogue/"
    data = {"offset": {"start": 0, "size": 1000}, "sort_by": "recent", **filters}

    return session.post_request(url=url, json=data, allow_redirect=True)


def get_latest_dataset_metadata(session: DAFNISession, version_id: str) -> dict:
    """Function to get the dataset metadata for a given dataset

    Args:
        session (str): User session
        version_id (str): Dataset Version ID

    Returns:
        dict: Dataset Version Metadata dict

    Raises:
        ResourceNotFoundError: If a dataset with the given id wasn't found
    """
    url = f"{NID_API_URL}/nid/metadata/{version_id}"

    try:
        return session.get_request(url=url, allow_redirect=True)
    except EndpointNotFoundError as err:
        # When the endpoint isn't found it means a dataset with the given id's
        # wasn't found
        raise ResourceNotFoundError(
            f"Unable to find a dataset with version_id '{version_id}'"
        ) from err


# TODO: This is needed due to a bug, remove once fixed
def _upload_dataset_metadata_error_message_func(session: DAFNISession):
    """Custom error message parser used here due to a bug meaning all
    errors for the dataset metadata upload endpoints are returned under
    a dictionary named "metadata

    This returns a function that will parse errors from this if they are
    not found automatically."""

    def error_message_func(response: requests.Response):
        try:
            error_message = session.get_error_message(response)

            if error_message is None:
                decoded_response = response.json()

                if "metadata" in decoded_response:
                    # This returns a list of errors, add them all to the
                    # message
                    error_message = "Found errors in metadata:"
                    for error in decoded_response["metadata"]:
                        error_message += f"\n{error}"

            return error_message
        except requests.JSONDecodeError:
            return None

    return error_message_func


def upload_dataset_metadata(
    session: DAFNISession,
    temp_bucket_id: str,
    metadata: dict,
    dataset_id: Optional[str] = None,
) -> requests.Response:
    """Uploads dataset metadata to the NID

    This will commit the dataset and triggers the deletion of the temporary
    bucket when successful.

    Args:
        session (DAFNISession): User session
        temp_bucket_id (str): Minio temporary bucket ID
        metadata (dict): Dataset metadata
        dataset_id (Optional[str]): Dataset ID if uploading a new version of
                                    an existing dataset (Default: None)

    Raises:
        EndpointNotFoundError: If the post request returns a 404 status
                               code
        DAFNIError: If an error occurs with an error message from DAFNI
        HTTPError: If any other error occurs without an error message from
                   DAFNI

    Returns:
        Response: Upload Response
    """

    if dataset_id:
        url = f"{NID_API_URL}/nid/dataset/{dataset_id}"
    else:
        url = f"{NID_API_URL}/nid/dataset/"
    data = {"bucketId": temp_bucket_id, "metadata": metadata}
    return session.post_request(
        url=url,
        json=data,
        error_message_func=_upload_dataset_metadata_error_message_func(session),
    )


def upload_dataset_metadata_version(
    session: DAFNISession,
    dataset_id: str,
    version_id: str,
    metadata: dict,
) -> requests.Response:
    """Uploads a new version of a dataset's metadata to the NID

    Args:
        session (DAFNISession): User session
        dataset_id (str): Dataset ID
        version_id (str): Dataset version ID
        metadata (dict): Dataset metadata

    Raises:
        EndpointNotFoundError: If the post request returns a 404 status
                               code
        DAFNIError: If an error occurs with an error message from DAFNI
        HTTPError: If any other error occurs without an error message from
                   DAFNI

    Returns:
        Response: Upload Response
    """
    url = f"{NID_API_URL}/nid/metadata/{dataset_id}/{version_id}"
    data = {"metadata": metadata}
    return session.post_request(
        url=url,
        json=data,
        error_message_func=_upload_dataset_metadata_error_message_func(session),
    )


def delete_dataset(session: DAFNISession, dataset_id: str) -> Response:
    """Calls the NID to delete a dataset

    Args:
        session (DAFNISession): User session
        dataset_id (str): Dataset ID for the selected dataset
    """
    url = f"{NID_API_URL}/nid/dataset/{dataset_id}"
    return session.delete_request(url)


def delete_dataset_version(session: DAFNISession, version_id: str) -> Response:
    """Calls the NID to delete a dataset version

    Args:
        session (DAFNISession): User session
        version_id (str): Dataset version ID for the selected dataset version
    """
    url = f"{NID_API_URL}/nid/version/{version_id}/"
    return session.delete_request(url)
