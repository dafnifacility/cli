###############################################################################
# Workflows API
###############################################################################
#
# Uses the API definition at https://dafni-nims-api.secure.dafni.rl.ac.uk/swagger/
#
###############################################################################


import json
from pathlib import Path
from typing import List, Tuple

from requests import Response

from dafni_cli.api.dafni_api import (
    dafni_delete_request,
    dafni_get_request,
    dafni_post_request,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import WORKFLOWS_API_URL


def get_all_workflows(session: DAFNISession) -> List[dict]:
    """
    Call the "workflows_list" endpoint and return the resulting list of dictionaries.

    Args:
        session (DAFNISession): User session

    Returns:
        List[dict]: list of dictionaries with raw response from API
    """
    url = WORKFLOWS_API_URL + "/workflows/"
    return dafni_get_request(url, session)


def get_workflow(session: DAFNISession, workflow_version_id: str) -> dict:
    """
    Call the "workflows" endpoint and return the resulting dictionary.

    Args:
        session (DAFNISession): User session
        workflow_version_id (str): workflow version ID for selected workflow

    Returns:
        dict: dictionary for the details of selected workflow
    """
    url = WORKFLOWS_API_URL + "/workflows/" + workflow_version_id + "/"
    return dafni_get_request(url, session)


def upload_workflow(
    session: DAFNISession, file_path: Path, version_message: str, parent_id: str
) -> Tuple[str, dict]:
    """
    Uploads a DAFNI workflow specified in a JSON file

    Args:
        session (DAFNISession): User session
        file_path: Path to the workflow definition file (JSON)
        version_message: String describing the new version, which will overwrite any version message in the JSON description
        parent_id: The ID of the parent workflow, for updating an existing workflow

    Returns:
        str: The ID for the upload
        dict: The urls for the definition and image with keys "definition" and "image", respectively.
    """
    if parent_id:
        url = WORKFLOWS_API_URL + "/workflows/" + parent_id + "/upload/"
    else:
        url = WORKFLOWS_API_URL + "/workflows/upload/"
    with open(file_path, "r") as f:
        workflow_description = json.load(f)
        if version_message:
            workflow_description["version_message"] = version_message
        return dafni_post_request(url, session, workflow_description)


# TODO rename so different names and see if used
# def upload_workflow(jwt: str, workflow_description: dict) -> Tuple[str, dict]:
#    """
#    Uploads a DAFNI workflow specified in a dictionary to the platform
#
#    Args:
#        jwt (str): JWT
#        workflow_description: A dictionary containing the workflow
#
#    Returns:
#        str: The ID for the upload
#        dict: The urls for the definition and image with keys "definition" and "image", respectively.
#    """
#    url = WORKFLOWS_API_URL + "/workflows/upload/"
#    print(workflow_description)
#    return dafni_post_request(url, jwt, workflow_description)


def delete_workflow(session: DAFNISession, workflow_version_id: str) -> Response:
    """
    Calls the workflows_delete endpoint

    Args:
        session (DAFNISession): User session
        workflow_version_id (str): version ID of workflow to be deleted
    """
    url = WORKFLOWS_API_URL + "/workflows/" + workflow_version_id
    return dafni_delete_request(url, session)
