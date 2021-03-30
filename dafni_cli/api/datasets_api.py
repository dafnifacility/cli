from typing import List

from dafni_cli.consts import DISCOVERY_API_URL
from dafni_cli.api.dafni_api import dafni_get_request, dafni_post_request


def get_all_datasets(jwt: str, filters: dict) -> List[dict]:
    """Function to retrieve all datasets available to the
    given user

    Args:
        jwt (str): Users JWT
        filters (dict): dict of filters to apply to the get datasets query

    Returns:
        List[dict]: List of available datasets
    """
    url = DISCOVERY_API_URL + "/catalogue/"
    data = {"offset": {"start": 0, "size": 1000}, "sort_by": "recent", **filters}

    return dafni_post_request(url, jwt, data, allow_redirect=True)


def get_latest_dataset_metadata(jwt: str, dataset_id: str, version_id: str) -> dict:
    """Function to get the dataset metadata for a given dataset

    Args:
        jwt (str): Users JWT
        dataset_id (str): Dataset ID
        version_id (str): Dataset Version ID

    Returns:
        dict: Dataset Version Metadata dict
    """
    url = f"{DISCOVERY_API_URL}/metadata/{dataset_id}/{version_id}"
    return dafni_get_request(url, jwt, allow_redirect=True)
