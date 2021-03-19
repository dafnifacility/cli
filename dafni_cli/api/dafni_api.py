import requests
from typing import Union, List

from dafni_cli.consts import MODELS_API_URL, DISCOVERY_API_URL


def dafni_get_request(
    url: str, jwt: str, allow_redirect: bool = False
) -> Union[list, dict]:
    """Performs a GET request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        jwt (str): JWT
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.

    Returns:
        list: For an endpoint returning several objects, a list is returned (e.g. /models/).
        dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
    """
    response = requests.get(
        url,
        headers={"Content-Type": "application/json", "authorization": jwt},
        allow_redirects=allow_redirect,
    )
    response.raise_for_status()
    return response.json()


def dafni_post_request(
    url: str, jwt: str, data: dict, allow_redirect: bool = False
) -> List[dict]:
    """Performs a POST request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        jwt (str): JWT
        data (dict): The data to be POSTed in JSON format
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.

    Returns:
        List[dict]: For an endpoint returning several objects, a list is returned (e.g. /catalogue/)
    """
    response = requests.post(
        url,
        headers={"Content-Type": "application/json", "authorization": jwt},
        allow_redirects=allow_redirect,
        json=data,
    )
    response.raise_for_status()
    return response.json()
