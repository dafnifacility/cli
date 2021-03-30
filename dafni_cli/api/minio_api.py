from requests import Response
from pathlib import Path
from typing import List

from dafni_cli.consts import MINIO_UPLOAD_CT, DATA_UPLOAD_API_URL
from dafni_cli.api.dafni_api import (
    dafni_post_request,
    dafni_patch_request,
    dafni_put_request,
)


def upload_file_to_minio(jwt: str, url: str, file_path: Path) -> Response:
    """Function to upload definition or image files to DAFNI

    Args:
        jwt (str): JWT
        url (str): URL to upload the file to
        file_path (Path): Path to the file

    Returns:
        Response: Response returned from the put request
    """
    content_type = MINIO_UPLOAD_CT
    with open(file_path, "rb") as file_data:
        return dafni_put_request(url, jwt, file_data, content_type)


def get_data_upload_id(jwt: str) -> str:
    """Function to get a temporary upload ID from
    DAFNI data upload API

    Args:
        jwt (str): Users JWT

    Returns:
        str: Temporary Upload ID
    """

    url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
    data = {"cancelToken": {"promise": {}}}

    return dafni_post_request(url, jwt, data, allow_redirect=True)


def get_data_upload_urls(jwt: str, upload_id: str, file_names: List[str]) -> dict:
    """Function to get an upload URL for each file name given.
    Returns a nested dict under the 'URLs' key, with each key being the file name,
    and the value being the upload URL

    Args:
        jwt (str): Users JWT
        upload_id (str): Temporary Upload ID for the Upload API
        file_names (List[str]): List of all file names to upload

    Returns:
        dict: Dict containing a url for each given file name
    """
    url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
    data = {"bucketId": upload_id, "datafiles": file_names}

    return dafni_patch_request(url, jwt, data, allow_redirect=True)


def upload_dataset_metadata(jwt, upload_id: str, metadata: dict) -> Response:
    """Function to upload Dataset Metadata to Minio

    Args:
        jwt ([type]): Users JWT
        upload_id (str): Minio Temporary Upload ID
        metadata (dict): Dataset Metadata

    Returns:
        Response: Upload Response
    """
    url = f"{DATA_UPLOAD_API_URL}/nid/dataset/"
    data = {"bucketId": upload_id, "metadata": metadata}
    return dafni_post_request(url, jwt, data, raise_status=False)