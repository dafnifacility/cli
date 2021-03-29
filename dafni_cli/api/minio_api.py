from requests import Response
from pathlib import Path

from dafni_cli.consts import MINIO_UPLOAD_CT
from dafni_cli.api.dafni_api import dafni_put_request


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