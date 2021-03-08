import requests
from requests import Response
from typing import Union, List
from dafni_cli.urls import MODELS_API_URL


def dafni_get_request(url: str, jwt: str) -> Union[dict, List]:
    """Helper function to make get requests with a JWT
    to the DAFNI API's

    Args:
        url (str): url of API end point
        jwt (str): Authentication JWT for the user

    Returns:
        Union[dict, List]: processed request response
    """
    response = requests.get(
        url,
        headers={"Content-Type": "application/json", "authorization": jwt},
        allow_redirects=False,
    )
    response.raise_for_status()
    return response.json()


def get_models_dicts(jwt: str) -> List[dict]:
    """Function to call the list models endpoint and return the resulting list of dictionaries.

    Args:
        jwt (str): JWT

    Returns:
        List[dict]: list of dictionaries with raw response from API
    """
    url = MODELS_API_URL + "/models/"
    return dafni_get_request(url, jwt)


def get_single_model_dict(jwt: str, model_version_id: str) -> dict:
    """Function to call the get model details endpoint and return the resulting dictionary.

    Args:
        jwt (str): JWT
        model_version_id (str): model version ID for selected model

    Returns:
        dict: dictionary for the details of selected model
    """
    url = MODELS_API_URL + "/models/" + model_version_id + "/"
    return dafni_get_request(url, jwt)


def get_model_metadata_dicts(jwt: str, model_version_id: str) -> dict:
    """Function to call the get model metadata endpoint and return the resulting dictionary.

    Args:
        jwt (str): JWT
        model_version_id (str): model version ID for selected model

    Returns:
        dict: dictionary for the metadata of selected model
    """
    url = MODELS_API_URL + "/models/" + model_version_id + "/definition/"
    return dafni_get_request(url, jwt)