from pathlib import Path
from typing import List, Union

import requests

from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import (
    DATA_DOWNLOAD_API_URL,
    DATA_DOWNLOAD_REDIRECT_API_URL,
    DATA_UPLOAD_API_URL,
    MINIO_UPLOAD_CT,
)


def upload_file_to_minio(
    session: DAFNISession, url: str, file_path: Path
) -> requests.Response:
    """Function to upload definition or image files to DAFNI

    Args:
        session (DAFNISession): User session
        url (str): URL to upload the file to
        file_path (Path): Path to the file

    Returns:
        Response: Response returned from the put request
    """
    with open(file_path, "rb") as file_data:
        return session.put_request(
            url=url, content_type=MINIO_UPLOAD_CT, data=file_data
        )


def get_data_upload_id(session: DAFNISession) -> str:
    """Function to get a temporary upload ID from
    DAFNI data upload API

    Args:
        session (str): User session

    Returns:
        str: Temporary Upload ID
    """

    url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
    # TODO remove this - no cancel tokens in cli - this is front-end-y
    data = {"cancelToken": {"promise": {}}}

    return session.post_request(url=url, json=data, allow_redirect=True)


def get_data_upload_urls(
    session: DAFNISession, upload_id: str, file_names: List[str]
) -> dict:
    """Function to get an upload URL for each file name given.
    Returns a nested dict under the 'URLs' key, with each key being the file name,
    and the value being the upload URL

    Args:
        session (DAFNISession): User session
        upload_id (str): Temporary Upload ID for the Upload API
        file_names (List[str]): List of all file names to upload

    Returns:
        dict: Dict containing a url for each given file name
    """
    url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
    data = {"bucketId": upload_id, "datafiles": file_names}

    return session.patch_request(url=url, data=data, allow_redirect=True)


def upload_dataset_metadata(
    session: DAFNISession, upload_id: str, metadata: dict
) -> requests.Response:
    """Function to upload Dataset Metadata to Minio

    Args:
        session (DAFNISession): User session
        upload_id (str): Minio Temporary Upload ID
        metadata (dict): Dataset Metadata

    Returns:
        Response: Upload Response
    """
    url = f"{DATA_UPLOAD_API_URL}/nid/dataset/"
    data = {"bucketId": upload_id, "metadata": metadata}
    return session.post_request(url=url, json=data, raise_status=False)


def minio_get_request(
    url: str, session: DAFNISession, allow_redirect: bool = False, content: bool = False
) -> Union[List[dict], dict, bytes]:
    """
    GET data file from minio. If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        session (DAFNISession): User session
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
        content (bool): Flag to define if the response content is returned. default is the response json

    Returns:
        dict: For an endpoint returning one object, this will be a dictionary.
    """
    # Substitute the minio URL returned in the request string with a
    file_url = url.replace(DATA_DOWNLOAD_API_URL, DATA_DOWNLOAD_REDIRECT_API_URL)
    return session.get_request(
        file_url,
        content_type="application/json",
        allow_redirect=allow_redirect,
        content=content,
        raise_status=True,
    )
