from typing import List

from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import DISCOVERY_API_URL


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
    url = DISCOVERY_API_URL + "/catalogue/"
    data = {"offset": {"start": 0, "size": 1000}, "sort_by": "recent", **filters}

    return session.post_request(url=url, json=data, allow_redirect=True)


# TODO: Make dataset_id optional? - Can search just by version ID now
def get_latest_dataset_metadata(
    session: DAFNISession, dataset_id: str, version_id: str
) -> dict:
    """Function to get the dataset metadata for a given dataset

    Args:
        session (str): User session
        dataset_id (str): Dataset ID
        version_id (str): Dataset Version ID

    Returns:
        dict: Dataset Version Metadata dict
    """
    url = f"{DISCOVERY_API_URL}/metadata/{dataset_id}/{version_id}"
    return session.get_request(url, allow_redirect=True)
