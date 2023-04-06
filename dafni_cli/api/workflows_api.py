###############################################################################
# Workflows API
###############################################################################
#
# Uses the API definition at https://dafni-nims-api.secure.dafni.rl.ac.uk/swagger/
#
###############################################################################


import json
from tokenize import String
from requests import Response
from typing import List, Tuple
from pathlib import Path

from dafni_cli.consts import WORKFLOWS_API_URL
from dafni_cli.api.dafni_api import (
    dafni_get_request,
    dafni_post_request,
    dafni_delete_request
)


# TODO align function naming
def get_all_workflows_dicts(jwt: str) -> List[dict]:
    """
    Call the "workflows_list" endpoint and return the resulting list of dictionaries.

    Args:
        jwt (str): JWT

    Returns:
        List[dict]: list of dictionaries with raw response from API
    """
    url = WORKFLOWS_API_URL + "/workflows/"
    return dafni_get_request(url, jwt)


def get_single_workflow_dict(jwt: str, workflow_version_id: str) -> dict:
    """
    Call the "workflows_read" endpoint and return the resulting dictionary.

    Args:
        jwt (str): JWT
        workflow_version_id (str): workflow version ID for selected workflow

    Returns:
        dict: dictionary for the details of selected workflow
    """
    url = WORKFLOWS_API_URL + "/workflows/" + workflow_version_id + "/"
    return dafni_get_request(url, jwt)


def upload_workflow(
    jwt: str, file_path: Path, version_message: str, parent_id: str
) -> Tuple[str, dict]:
    """
    Uploads a DAFNI workflow specified in a JSON file

    Args:
        jwt (str): JWT
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
        return dafni_post_request(url, jwt, workflow_description)


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


def delete_workflow(jwt: str, workflow_version_id: str) -> Response:
    """
    Calls the workflows_delete endpoint

    Args:
        jwt (str): JWT
        workflow_version_id (str): version ID of workflow to be deleted
    """
    url = WORKFLOWS_API_URL + "/workflows/" + workflow_version_id
    return dafni_delete_request(url, jwt)


def execute_workflow(jwt: str, workflow_version_id: str, parameter_set_id: str = None):
    """
    Executes a workflow, with an optional parameter set ID

    Args:
        jwt (str): JWT
        workflow_version_id (str): workflow version ID to be executed
    """
    url = WORKFLOWS_API_URL + "/workflows/execute/" \
        + workflow_version_id + "/" \
        + parameter_set_id + "/"
    data = {}
    
    return dafni_post_request(url, jwt, data, raise_status = False)
    