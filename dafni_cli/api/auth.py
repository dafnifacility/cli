from dataclasses import dataclass
from typing import ClassVar, List, Optional

from dafni_cli.api.parser import ParserBaseObject, ParserParam


@dataclass
class Auth(ParserBaseObject):
    """Dataclass representing the access the user has for a DAFNI resource
       (found in models and workflows)

    Attributes:
        view (bool): View access
        read (bool): Read access
        update (bool): Update access
        destroy (bool): Deletion access
        reason (str): Reason user has access to view this model


        The following are only present for the /model/<version_id> or
        /workflow/<version_id> endpoints (but are guaranteed not to be
        None for them)
        --------
        asset_id (Optional[str]): ID of the model


        The following are only present for the /models or /workflows endpoint
        (but are guaranteed not to be None for them)
        --------
        role_id (Optional[str]): Role ID of the user
        name (Optional[str]): Name associated with the auth type
    """

    view: bool
    read: bool
    update: bool
    destroy: bool
    reason: str

    asset_id: Optional[str] = None

    role_id: Optional[str] = None
    name: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("view", "view"),
        ParserParam("read", "read"),
        ParserParam("update", "update"),
        ParserParam("destroy", "destroy"),
        ParserParam("reason", "reason", str),
        ParserParam("asset_id", "asset_id", str),
        ParserParam("role_id", "role_id", str),
        ParserParam("name", "name", str),
    ]

    def get_permission_string(self) -> str:
        """Return a string representing the permissions this auth object
        allows (Taken from front-end)"""

        if self.read and self.view:
            return "Full access"
        elif not self.read and self.view:
            return "View only"
        return "Not visible"
