from typing import BinaryIO, List, Union

from requests import Response

from dafni_cli.api.session import DAFNISession


# TODO have same optional flags for each function
def dafni_get_request(
    url: str, session: DAFNISession, allow_redirect: bool = False, content: bool = False
) -> Union[List[dict], dict, bytes]:
    """Performs a GET request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        session (DAFNISession): User session
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
        content (bool): Flag to define if the response content is returned. default is the response json

    Returns:
        List[dict]: For an endpoint returning several objects, a list is returned (e.g. /models/).
        dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
    """
    return session.get_request(
        url,
        headers={"Content-Type": "application/json"},
        allow_redirect=allow_redirect,
        content=content,
        raise_status=True,
    )


def dafni_post_request(
    url: str,
    session: DAFNISession,
    data: dict,
    allow_redirect: bool = False,
    raise_status: bool = True,
) -> Union[List[dict], dict]:
    """Performs a POST request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        session (DAFNISession): User session
        data (dict): The data to be POSTed in JSON format
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
        raise_status (bool) Flag to define if failure status' should be raised as HttpErrors. Default is True.

    Returns:
        List[dict]: For an endpoint returning several objects, a list is returned (e.g. /catalogue/)
        dict: For an endpoint requesting upload urls (e.g. /models/upload/)
    """

    return session.post_request(
        url,
        headers={"Content-Type": "application/json"},
        json=data,
        allow_redirect=allow_redirect,
        raise_status=raise_status,
    )


def dafni_put_request(
    url: str,
    session: DAFNISession,
    data: BinaryIO,
    content_type: str = "application/yaml",
) -> Response:
    """Performs a PUT request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        session (DAFNISession): User session
        data (BinaryIO): The data to be PUT-ed
        content_type (str): Content type for the headers (e.g. "application/yaml")

    Returns:
        Response: Response from API
    """
    return session.put_request(
        url, headers={"Content-Type": content_type}, data=data, raise_status=True
    )


def dafni_patch_request(
    url: str, session: DAFNISession, data: dict, allow_redirect: bool = False
) -> Union[List[dict], dict]:
    """Performs a PATCH request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        session (DAFNISession): User session
        data (dict): The data to be POSTed in JSON format
        allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.

    Returns:
        List[dict]: For an endpoint returning several objects, a list is returned (e.g. /catalogue/)
        dict: For an endpoint requesting upload urls (e.g. /models/upload/)
    """
    return session.patch_request(
        url,
        headers={"Content-Type": "application/json"},
        allow_redirect=allow_redirect,
        data=data,
        raise_status=True,
    )


def dafni_delete_request(url: str, session: DAFNISession) -> Response:
    """Performs a DELETE request from the DAFNI API.
    If a status other than 200 is returned, an exception will be raised.

    Args:
        url (str): The url endpoint that is being queried
        session (DAFNISession): User session

    Returns:
        Response: Response from the API
    """
    return session.delete_request(url, headers={}, raise_status=True)
