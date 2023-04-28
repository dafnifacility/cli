class LoginError(Exception):
    """Generic error to distinguish login failures"""


class DAFNIError(Exception):
    """An error returned by one of the DAFNI API's"""


class EndpointNotFoundError(Exception):
    """An error distinguishing when an endpoint is not found"""


class ResourceNotFoundError(Exception):
    """An error distinguishing when a resource was not found"""
