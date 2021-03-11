import requests
from typing import Union, List

from dafni_cli.consts import MODELS_API_URL, DISCOVERY_API_URL
from dafni_cli.api.dafni_api import dafni_get_request


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


def get_all_datasets(jwt: str) -> List[dict]:
    """Function to retrieve all datasets available to the
    given user

    Args:
        jwt (str): Users JWT

    Returns:
        List[dict]: List of available datasets
    """
    url = DISCOVERY_API_URL + "/catalogue/"
    return dafni_get_request(url, jwt, allow_redirect=True)