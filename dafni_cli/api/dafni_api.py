import requests
from typing import Union, List, BinaryIO
from requests import Response

from dafni_cli.consts import MODELS_API_URL, DISCOVERY_API_URL


def dafni_get_request(
    url: str, jwt: str, allow_redirect: bool = False, content: bool = False
) -> Union[List[dict], dict]:
    """Performs a GET request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        jwt (str): JWT
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
        content (bool): Flag to define if the response content is returned. default is the response json

    Returns:
        List[dict]: For an endpoint returning several objects, a list is returned (e.g. /models/).
        dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
    """
    response = requests.get(
        url,
        headers={"Content-Type": "application/json", "authorization": jwt},
        allow_redirects=allow_redirect,
    )
    response.raise_for_status()

    if content:
        return response.content

    return response.json()


def dafni_post_request(
    url: str, jwt: str, data: dict, allow_redirect: bool = False
) -> Union[List[dict], dict]:
    """Performs a POST request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        jwt (str): JWT
        data (dict): The data to be POSTed in JSON format
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.

    Returns:
        List[dict]: For an endpoint returning several objects, a list is returned (e.g. /catalogue/)
        dict: For an endpoint requesting upload urls (e.g. /models/upload/)
    """
    response = requests.post(
        url,
        headers={"Content-Type": "application/json", "authorization": jwt},
        allow_redirects=allow_redirect,
        json=data,
    )
    response.raise_for_status()
    return response.json()


def dafni_put_request(
    url: str, jwt: str, data: BinaryIO, content_type: str = "application/yaml"
) -> Response:
    """Performs a PUT request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        jwt (str): JWT
        data (BinaryIO): The data to be PUT-ed
        content_type (str): Content type for the headers (e.g. "application/yaml")

    Returns:
        Response: Response from API
    """
    response = requests.put(
        url,
        headers={"Content-Type": content_type, "authorization": jwt},
        data=data,
    )
    response.raise_for_status()
    return response


def dafni_delete_request(url: str, jwt: str) -> Response:
    """Performs a DELETE request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        jwt (str): JWT

    Returns:
        Response: Response from the API
    """
    response = requests.delete(url, headers={"authorization": jwt})
    response.raise_for_status()
    return response
