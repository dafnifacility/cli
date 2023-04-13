from typing import Optional

from dafni_cli.utils import check_key_in_dict


class Auth:
    """
    Contains the authorisation details that a user has for a DAFNI entity.

    Methods:

    Attributes:
        asset_id (str): ID of the entity
        destroy (bool): Deletion access
        name (str): Name
        read (bool): Read access
        reason (str): Reason you have access to view this entity
        update (bool): Update access
        view (bool): View access
    """

    destroy = None

    def __init__(self, auth_dict: Optional[dict] = None):
        """Auth Constructor

        Args:
            auth_dict (Optional[dict]): auth dictionary found in model and dataset dictionaries
        """
        self.asset_id = None
        self.destroy = False
        self.name = None
        self.read = False
        self.reason = None
        self.update = False
        self.view = False

        if auth_dict:
            self.set_attributes_from_dict(auth_dict)

    def set_attributes_from_dict(self, auth_dict: dict):
        """Function to set the Auth attributes based on a given auth dictionary

        Args:
            auth_dict (dict): auth dictionary found in model and dataset dictionaries
        """
        self.asset_id = check_key_in_dict(auth_dict, ["asset_id"], default=None)
        self.destroy = check_key_in_dict(auth_dict, ["destroy"], default=False)
        self.name = check_key_in_dict(auth_dict, ["name"], default=None)
        self.read = check_key_in_dict(auth_dict, ["read"], default=False)
        self.reason = check_key_in_dict(auth_dict, ["reason"], default=None)
        self.update = check_key_in_dict(auth_dict, ["update"], default=False)
        self.view = check_key_in_dict(auth_dict, ["view"], default=False)
