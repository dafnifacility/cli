from pathlib import Path
from typing import Dict, List, Union

import requests
from tqdm import tqdm

from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import (
    DSS_API_URL,
    MINIO_API_URL,
    MINIO_DOWNLOAD_REDIRECT_API_URL,
    MINIO_UPLOAD_CT,
    NID_API_URL,
)


def upload_file_to_minio(
    session: DAFNISession, url: str, file_path: Path, progress_bar=False
) -> requests.Response:
    """Function to upload definition or image files to DAFNI

    Args:
        session (DAFNISession): User session
        url (str): URL to upload the file to
        file_path (Path): Path to the file
        progress_bar (bool): Whether to display a progress bar for the file
                             using tqdm

    Returns:
        Response: Response returned from the put request
    """

    with tqdm.wrapattr(
        open(file_path, "rb"),
        "read",
        desc=file_path.name,
        miniters=1,
        total=file_path.stat().st_size,
        disable=not progress_bar,
    ) as file_data:
        return session.put_request(
            url=url,
            content_type=MINIO_UPLOAD_CT,
            data=file_data,
        )


def create_temp_bucket(session: DAFNISession) -> str:
    """Creates a temporary bucket and returns its ID using
    DAFNI data upload API

    Args:
        session (str): User session

    Returns:
        str: Minio temporary bucket ID
    """

    url = f"{NID_API_URL}/nid/upload/"

    return session.post_request(url=url, allow_redirect=True)


def delete_temp_bucket(session: DAFNISession, temp_bucket_id: str):
    """Deletes a temporary bucket given its ID

    Args:
        temp_bucket_id (str): Minio temporary bucket ID
    """

    # Strip out 'temp-' which will be present in the ID returned by
    # create_temp_bucket
    url = f"{DSS_API_URL}/assets/{temp_bucket_id.replace('temp-', '')}"

    return session.delete_request(url=url)


def get_data_upload_urls(
    session: DAFNISession, temp_bucket_id: str, file_names: List[str]
) -> dict:
    """Returns an upload URL for each file name given

    Returns a nested dict under the 'URLs' key, with each key being the file name,
    and the value being the upload URL

    Args:
        session (DAFNISession): User session
        temp_bucket_id (str): ID of the temporary Minio bucket to upload to
        file_names (List[str]): List of all file names to upload

    Returns:
        dict: Dict containing a url for each given file name
    """
    url = f"{NID_API_URL}/nid/upload/"
    data = {"bucketId": temp_bucket_id, "datafiles": file_names}

    return session.patch_request(url=url, json=data, allow_redirect=True)


def minio_get_request(
    session: DAFNISession, url: str, stream: bool = False
) -> Union[Dict, List[Dict], requests.Response]:
    """Get a data file from Minio

    Args:
        session (DAFNISession): User session
        url (str): The url endpoint that is being queried
        stream (bool): Whether to stream the request. In this case will
                       return the response object itself rather than the
                       json.
    Returns:
        Dict: When 'stream' is False for endpoints returning one object
              e.g. /models/<version_id>
        List[Dict]: When 'stream' is False for endpoints returning multiple
                    objects e.g. /models/
        requests.Response: When 'stream' is True - The whole response object
    """
    # Substitute the Minio URL returned in the request string with a redirect
    file_url = url.replace(MINIO_API_URL, MINIO_DOWNLOAD_REDIRECT_API_URL)
    return session.get_request(
        url=file_url,
        content_type="application/json",
        allow_redirect=False,
        stream=stream,
    )
