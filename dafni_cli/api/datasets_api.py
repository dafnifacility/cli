import requests
from typing import Union, List

from dafni_cli.consts import MODELS_API_URL, DISCOVERY_API_URL
from dafni_cli.api.dafni_api import dafni_get_request, dafni_post_request


def get_all_datasets(jwt: str) -> List[dict]:
    """Function to retrieve all datasets available to the
    given user

    Args:
        jwt (str): Users JWT

    Returns:
        List[dict]: List of available datasets
    """
    url = DISCOVERY_API_URL + "/catalogue/"
    data = {"offset": {"start": 0, "size": 1000}, "sort_by": "recent"}

    return dafni_post_request(url, jwt, data, allow_redirect=True)
