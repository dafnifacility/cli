###############################################################################
# Workflows API
###############################################################################
#
# Uses the API definition at https://dafni-nims-api.secure.dafni.rl.ac.uk/swagger/
#
###############################################################################


import json
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from requests import Response

from dafni_cli.api.exceptions import (
    DAFNIError,
    EndpointNotFoundError,
    ResourceNotFoundError,
    ValidationError,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import NIMS_API_URL
from dafni_cli.utils import construct_validation_errors_from_dict


def get_all_workflows(session: DAFNISession) -> List[dict]:
    """Function to retrieve all workflows available to the user

    Args:
        session (DAFNISession): User session

    Returns:
        List[dict]: List of dictionaries with raw response from API
    """
    url = f"{NIMS_API_URL}/workflows/"
    return session.get_request(url)


def get_workflow(session: DAFNISession, version_id: str) -> dict:
    """Function to get the details of a workflows

    Args:
        session (DAFNISession): User session
        version_id (str): Workflow version ID for selected workflow

    Returns:
        dict: Dictionary containing the details of the workflow

    Raises:
        ResourceNotFoundError: If a workflow with the given version_id wasn't
                               found
    """
    url = f"{NIMS_API_URL}/workflows/{version_id}/"

    try:
        return session.get_request(url)
    except EndpointNotFoundError as err:
        # When the endpoint isn't found it means the workflow wasn't found
        raise ResourceNotFoundError(
            f"Unable to find a workflow with version id '{version_id}'"
        ) from err


def get_workflow_instance(session: DAFNISession, instance_id: str):
    """Function to get the details of a workflow instance

    Args:
        session (DAFNISession): User session
        version_id (str): Instance ID for selected workflow instance

    Returns:
        dict: Dictionary containing details of the workflow instance

    Raises:
        ResourceNotFoundError: If a workflow instance with the given
                               instance_id wasn't found
    """

    url = f"{NIMS_API_URL}/workflows/instances/{instance_id}/"

    try:
        return session.get_request(url)
    except EndpointNotFoundError as err:
        # When the endpoint isn't found it means the workflow instance wasn't
        # found
        raise ResourceNotFoundError(
            f"Unable to find a workflow instance with instance id '{instance_id}'"
        ) from err


def upload_workflow(
    session: DAFNISession,
    file_path: Path,
    version_message: str,
    parent_id: Optional[str] = None,
) -> dict:
    """Uploads a DAFNI workflow specified in a JSON file

    Args:
        session (DAFNISession): User session
        file_path: Path to the workflow definition file (JSON)
        version_message: String describing the new version
        parent_id: The ID of the parent workflow, for updating an existing workflow

    Returns:
        dict: Contains information about the uploaded workflow
    """
    if parent_id:
        url = f"{NIMS_API_URL}/workflows/{parent_id}/upload/"
    else:
        url = f"{NIMS_API_URL}/workflows/upload/"
    with open(file_path, "r", encoding="utf-8") as file:
        workflow_definition = json.load(file)
        data = {"version_message": version_message, "definition": workflow_definition}
        return session.post_request(url=url, json=data)


def delete_workflow_version(session: DAFNISession, version_id: str) -> Response:
    """
    Deletes a workflow version

    Args:
        session (DAFNISession): User session
        version_id (str): version ID of workflow to be deleted
    """
    url = f"{NIMS_API_URL}/workflows/{version_id}/"
    return session.delete_request(url)


def _validate_parameter_set_definition_error_message_func(session: DAFNISession):
    """Custom error message parser used here only because the endpoint may
    also return a dictionary with errors e.g.

    {
        "api_version": [
            "This field is required."
        ],
        "kind": [
            "This field is required."
        ],
        "metadata": [
            "This field is required."
        ]
    }

    In such a case, we first check for any regular errors, and then use
    this dictionary to form the error string if there aren't any
    """

    def error_message_func(response: requests.Response):
        try:
            error_message = session.get_error_message(response)

            if error_message is None:
                decoded_response = response.json()
                error_message = "Found the following errors in the definition:\n"
                error_message += "\n".join(
                    construct_validation_errors_from_dict(decoded_response)
                )

            return error_message
        except requests.JSONDecodeError:
            return None

    return error_message_func


def validate_parameter_set_definition(
    session: DAFNISession, parameter_set_definition_path: Path
):
    """Validates a parameter set definition file

    Args:
        session (DAFNISession): User session
        parameter_set_definition_path (Path): Path to the parameter set
                                              definition file

    Raises:
        ValidationError: If the validation fails
    """

    url = f"{NIMS_API_URL}/workflows/parameter-set/validate/"
    with open(parameter_set_definition_path, "rb") as file:
        # For this endpoint we assume any error with a message is a validation
        # error
        try:
            session.post_request(
                url=url,
                data=file,
                error_message_func=_validate_parameter_set_definition_error_message_func(
                    session
                ),
            )
        except DAFNIError as err:
            raise ValidationError(
                "Parameter set definition validation failed with the following "
                f"message:\n\n{str(err)}"
            ) from err


def upload_parameter_set(
    session: DAFNISession, parameter_set_definition_path: Path
) -> dict:
    """Uploads a parameter set

    Args:
        session (DAFNISession): User session
        parameter_set_definition_path (Path): Path to the parameter set
                                              definition file

    Returns:
        dict: JSON from response returned in post request (Forms a
              WorkflowParameterSet)
    """
    url = f"{NIMS_API_URL}/workflows/parameter-set/upload/"
    with open(parameter_set_definition_path, "rb") as file:
        return session.post_request(
            url=url,
            data=file,
            error_message_func=_validate_parameter_set_definition_error_message_func(
                session
            ),
        )
