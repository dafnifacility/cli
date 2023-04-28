from pathlib import Path
from typing import List, Tuple

from requests import Response
from dafni_cli.api.exceptions import EndpointNotFoundError, ResourceNotFoundError

from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import MODELS_API_URL, VALIDATE_MODEL_CT


def get_all_models(session: DAFNISession) -> List[dict]:
    """
    Function to call the "models_list" endpoint and return the resulting list of dictionaries.

    Args:
        session (DAFNISession): User session

    Returns:
        List[dict]: list of dictionaries with raw response from API
    """
    url = MODELS_API_URL + "/models/"
    return session.get_request(url)


def get_model(session: DAFNISession, version_id: str) -> dict:
    """Function to call the "models_read" endpoint and return the resulting
    dictionary

    Args:
        session (DAFNISession): User session
        version_id (str): model version ID for selected model

    Returns:
        dict: dictionary for the details of selected model

    Raises:
        ResourceNotFoundError: If a model with the given version_id wasn't
                               found
    """
    url = MODELS_API_URL + "/models/" + version_id + "/"

    try:
        return session.get_request(url)
    except EndpointNotFoundError as err:
        # When the endpoint isn't found it means the model wasn't found
        raise ResourceNotFoundError(
            f"Unable to find a model with version id '{version_id}'"
        ) from err


def validate_model_definition(
    session: DAFNISession, model_definition: Path
) -> Tuple[bool, str]:
    """
    Validates the model definition file using the "models_validate_update" endpoint

    Args:
        session (DAFNISession): User session
        model_definition (Path): Path to the model definition file

    Returns:
        bool: Whether the model definition is valid or not
        List[str]: Errors encountered if the model definition file is not valid
    """
    content_type = VALIDATE_MODEL_CT
    url = MODELS_API_URL + "/models/validate/"
    with open(model_definition, "rb") as md:
        response = session.put_request(url=url, content_type=content_type, data=md)
    if response.json()["valid"]:
        return True, ""
    else:
        # TODO we should return all errors and have a generic way of returning errors in cli
        return False, response.json()["errors"][0]


def get_model_upload_urls(session: DAFNISession) -> Tuple[str, dict]:
    """
    Obtains the model upload urls from the "models_upload_create" endpoint

    Args:
        session (DAFNISession): User session

    Returns:
        str: The ID for the upload
        dict: The urls for the definition and image with keys "definition" and "image", respectively.
    """
    url = MODELS_API_URL + "/models/upload/"
    data = {"image": True, "definition": True}
    urls_resp = session.post_request(url=url, json=data)
    upload_id = urls_resp["id"]
    urls = urls_resp["urls"]
    return upload_id, urls


def model_version_ingest(
    session: DAFNISession, upload_id: str, version_message: str, model_id: str = None
) -> dict:
    """
    Ingests a new version of a model using the "models_upload_ingest_create" endpoint

    Args:
        session (DAFNISession): User session
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
    return session.post_request(url=url, json=data)


def delete_model(session: DAFNISession, version_id: str) -> Response:
    """
    Calls the "models_delete" endpoint

    Args:
        session (DAFNISession): User session
        version_id (str): Model version ID for selected model
    """
    url = MODELS_API_URL + "/models/" + version_id
    return session.delete_request(url)
