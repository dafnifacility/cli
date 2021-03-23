import requests
from typing import Union, List

from dafni_cli.consts import MODELS_API_URL, DISCOVERY_API_URL
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


def get_latest_dataset_metadata(jwt: str, id: str, version_id: str):

    url = "{0}/metadata/{1}/{2}".format(DISCOVERY_API_URL, id, version_id)
    return dafni_get_request(url, jwt, allow_redirect=True)
