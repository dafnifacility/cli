import requests
from typing import Union

from dafni_cli.consts import MODELS_API_URL


def dafni_get_request(url: str, jwt: str) -> Union[list, dict]:
    """Performs a GET request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        jwt (str): JWT

    Returns:
        list: For an endpoint returning several objects, a list is returned (e.g. /models/).
        dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
    """
    response = requests.get(
        url,
        headers={
            "Content-Type": "application/json",
            "authorization": jwt
        },
        allow_redirects=False
    )
    response.raise_for_status()
    return response.json()


def get_models_dicts(jwt: str) -> list:
    """Function to call the list models endpoint and return the resulting list of dictionaries.

    Args:
        jwt (str): JWT

    Returns:
        list: list of dictionaries with raw response from API
    """
    url = MODELS_API_URL + '/models/'
    return dafni_get_request(url, jwt)


def get_single_model_dict(jwt: str, model_version_id: str) -> dict:
    """Function to call the get model details endpoint and return the resulting dictionary.

        Args:
            jwt (str): JWT
            model_version_id (str): model version ID for selected model

        Returns:
            dict: dictionary for the details of selected model
        """
    url = MODELS_API_URL + '/models/' + model_version_id + "/"
    return dafni_get_request(url, jwt)


def get_model_metadata_dicts(jwt: str, model_version_id: str) -> dict:
    """Function to call the get model metadata endpoint and return the resulting dictionary.

        Args:
            jwt (str): JWT
            model_version_id (str): model version ID for selected model

        Returns:
            dict: dictionary for the metadata of selected model
        """
    url = MODELS_API_URL + '/models/' + model_version_id + "/definition/"
    return dafni_get_request(url, jwt)
