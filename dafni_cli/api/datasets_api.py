from typing import List, Optional

import requests

from dafni_cli.api.exceptions import EndpointNotFoundError, ResourceNotFoundError
from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import NID_API_URL, SEARCH_AND_DISCOVERY_API_URL


# TODO this should work with pagination - check
def get_all_datasets(session: DAFNISession, filters: dict) -> List[dict]:
    """Function to retrieve all datasets available to the
    given user

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
        ResourceNotFoundError: If a dataset with the given id's wasn't found
    """
    url = f"{SEARCH_AND_DISCOVERY_API_URL}/metadata/{version_id}"

    try:
        return session.get_request(url=url, allow_redirect=True)
    except EndpointNotFoundError as err:
        # When the endpoint isn't found it means a dataset with the given id's
        # wasn't found
        raise ResourceNotFoundError(
            f"Unable to find a dataset with version_id '{version_id}'"
        ) from err


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
    return session.post_request(url=url, json=data)


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
    return session.post_request(url=url, json=data)
