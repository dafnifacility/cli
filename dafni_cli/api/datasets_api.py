import requests
from typing import Union, List
import json

from dafni_cli.consts import MODELS_API_URL, DISCOVERY_API_URL, DATA_UPLOAD_API_URL
from dafni_cli.api.dafni_api import (
    dafni_get_request,
    dafni_post_request,
    dafni_patch_request,
)


def get_all_datasets(jwt: str, filters: dict) -> List[dict]:
    """Function to retrieve all datasets available to the
    given user

    Args:
        jwt (str): Users JWT
        filters (dict): dict of filters to apply to the get datasets query

    Returns:
        List[dict]: List of available datasets
    """
    url = DISCOVERY_API_URL + "/catalogue/"
    data = {"offset": {"start": 0, "size": 1000}, "sort_by": "recent", **filters}

    return dafni_post_request(url, jwt, data, allow_redirect=True)


def get_latest_dataset_metadata(jwt: str, dataset_id: str, version_id: str) -> dict:
    """Function to get the dataset metadata for a given dataset

    Args:
        jwt (str): Users JWT
        dataset_id (str): Dataset ID
        version_id (str): Dataset Version ID

    Returns:
        dict: Dataset Version Metadata dict
    """
    url = f"{DISCOVERY_API_URL}/metadata/{dataset_id}/{version_id}"
    return dafni_get_request(url, jwt, allow_redirect=True)


def get_dataset_upload_id(jwt: str):

    url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
    data = {"cancelToken": {"promise": {}}}

    return dafni_post_request(url, jwt, data, allow_redirect=True)


def get_dataset_upload_urls(jwt: str, upload_id: str, file_names: List[str]):

    url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
    data = {"bucketId": upload_id, "datafiles": file_names}
    return dafni_patch_request(url, jwt, data, allow_redirect=True)


def upload_dataset_metadata(jwt, upload_id: str, metadata: dict):
    url = f"{DATA_UPLOAD_API_URL}/nid/dataset/"
    data = {"bucketId": upload_id, "metadata": metadata}
    return dafni_post_request(url, jwt, data, raise_status=False)