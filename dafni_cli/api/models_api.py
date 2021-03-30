from requests import Response
from typing import List, Tuple
from pathlib import Path

from dafni_cli.consts import MODELS_API_URL, VALIDATE_MODEL_CT, MINIO_UPLOAD_CT
from dafni_cli.api.dafni_api import (
    dafni_get_request,
    dafni_post_request,
    dafni_put_request,
    dafni_delete_request,
)


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


def get_model_metadata_dict(jwt: str, model_version_id: str) -> dict:
    """Function to call the get model metadata endpoint and return the resulting dictionary.

    Args:
        jwt (str): JWT
        model_version_id (str): model version ID for selected model

    Returns:
        dict: dictionary for the metadata of selected model
    """
    url = MODELS_API_URL + "/models/" + model_version_id + "/definition/"
    return dafni_get_request(url, jwt)


def validate_model_definition(jwt: str, model_definition: Path) -> Tuple[bool, str]:
    """Validates the model definition file using a PUT to the DAFNI API

    Args:
        jwt (str): JWT
        model_definition (Path): Path to the model definition file

    Returns:
        bool: Whether the model definition is valid or not
        List[str]: Errors encountered if the model definition file is not valid
    """
    content_type = VALIDATE_MODEL_CT
    url = MODELS_API_URL + "/models/definition/validate/"
    with open(model_definition, "rb") as md:
        response = dafni_put_request(url, jwt, md, content_type)
    if response.json()["valid"]:
        return True, ""
    else:
        return False, response.json()["errors"][0]


def get_model_upload_urls(jwt: str) -> Tuple[str, dict]:
    """Obtains the model upload urls from the DAFNI API

    Args:
        jwt (str): JWT

    Returns:
        str: The ID for the upload
        dict: The urls for the definition and image with keys "definition" and "image", respectively.
    """
    url = MODELS_API_URL + "/models/upload/"
    data = {"image": True, "definition": True}
    urls_resp = dafni_post_request(url, jwt, data)
    upload_id = urls_resp["id"]
    urls = urls_resp["urls"]
    return upload_id, urls


def model_version_ingest(
    jwt: str, upload_id: str, version_message: str, model_id: str = None
) -> dict:
    """Ingests a new version of a model to DAFNI

    Args:
        jwt (str): JWT
        upload_id (str): Upload ID
        version_message (str): Message to be attached to this version
        model_id (str): ID of existing parent model if it exists

    Returns:
        dict: JSON from response returned in post request
    """
    if model_id:
        url = (
            MODELS_API_URL + "/models/" + model_id + "/upload/" + upload_id + "/ingest/"
        )
    else:
        url = MODELS_API_URL + "/models/upload/" + upload_id + "/ingest/"
    data = {"version_message": version_message}
    return dafni_post_request(url, jwt, data)


def delete_model(jwt: str, model_version_id: str) -> Response:
    """Calls the delete model endpoint.

    Args:
        jwt (str): JWT
        model_version_id (str): model version ID for selected model
    """
    url = MODELS_API_URL + "/models/" + model_version_id
    return dafni_delete_request(url, jwt)
