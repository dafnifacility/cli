from pathlib import Path
from typing import List, Optional, Tuple

from requests import Response

from dafni_cli.api.exceptions import (
    EndpointNotFoundError,
    ResourceNotFoundError,
    ValidationError,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import NIMS_API_URL, VALIDATE_MODEL_CT


def get_all_models(session: DAFNISession) -> List[dict]:
    """Function to call the "models_list" endpoint and return the resulting
    list of dictionaries.

    Args:
        session (DAFNISession): User session

    Returns:
        List[dict]: list of dictionaries with raw response from API
    """
    url = f"{NIMS_API_URL}/models/"
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
    url = f"{NIMS_API_URL}/models/{version_id}/"

    try:
        return session.get_request(url)
    except EndpointNotFoundError as err:
        # When the endpoint isn't found it means the model wasn't found
        raise ResourceNotFoundError(
            f"Unable to find a model with version id '{version_id}'"
        ) from err


def validate_model_definition(session: DAFNISession, model_definition_path: Path):
    """Validates the model definition file using the "models_validate_update"
    endpoint

    Args:
        session (DAFNISession): User session
        model_definition_path (Path): Path to the model definition file

    Raises:
        ValidationError: If the validation fails
    """
    content_type = VALIDATE_MODEL_CT
    url = f"{NIMS_API_URL}/models/validate/"
    with open(model_definition_path, "rb") as md:
        response = session.put_request(url=url, content_type=content_type, data=md)
    # This response returns a property "valid" and any errors found (although
    # without a failed status code so we need to do this separately)
    if not response.json()["valid"]:
        raise ValidationError(
            "Model definition validation failed with the following "
            f"message:\n\n{session.get_error_message(response)}\n\n"
            "See "
            "https://docs.secure.dafni.rl.ac.uk/docs/how-to/models/how-to-write-a-model-definition-file/ "
            "for guidance on writing a model definition file"
        )


def get_model_upload_urls(session: DAFNISession) -> Tuple[str, dict]:
    """Obtains the model upload urls from the "models_upload_create" endpoint

    Args:
        session (DAFNISession): User session

    Returns:
        str: The ID for the upload
        dict: The urls for the definition and image with keys "definition" and "image", respectively.
    """
    url = f"{NIMS_API_URL}/models/upload/"
    data = {"image": True, "definition": True}
    urls_resp = session.post_request(url=url, json=data)
    upload_id = urls_resp["id"]
    urls = urls_resp["urls"]
    return upload_id, urls


def model_version_ingest(
    session: DAFNISession,
    upload_id: str,
    version_message: str,
    model_id: Optional[str] = None,
) -> dict:
    """Ingests a new version of a model using the "models_upload_ingest_create"
    endpoint

    Args:
        session (DAFNISession): User session
        upload_id (str): Upload ID
        version_message (str): Message to be attached to this version
        model_id (str): ID of existing parent model if it exists

    Returns:
        dict: JSON from response returned in post request
    """
    if model_id:
        url = f"{NIMS_API_URL}/models/{model_id}/upload/{upload_id}/ingest/"
    else:
        url = f"{NIMS_API_URL}/models/upload/{upload_id}/ingest/"
    data = {"version_message": version_message}
    return session.post_request(url=url, json=data)


def delete_model_version(session: DAFNISession, version_id: str) -> Response:
    """Deletes a model version

    Args:
        session (DAFNISession): User session
        version_id (str): Model version ID for selected model
    """
    url = f"{NIMS_API_URL}/models/{version_id}/"
    return session.delete_request(url)
