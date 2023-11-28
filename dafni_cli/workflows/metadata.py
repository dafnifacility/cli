from dataclasses import dataclass
from typing import ClassVar, List, Optional

from dafni_cli.api.parser import ParserBaseObject, ParserParam


@dataclass
class WorkflowMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI workflows's metadata

    Attributes:
        display_name (str): The display name of the Workflow
        name (str): Name of the Workflow
        summary (str): A short summary of the Workflow

        The following are only present for the /workflow/<version_id> endpoint
        (but are guaranteed not to be None for it)
        --------
        publisher_id (Optional[str]): The name of the person or organisation who has
                            published the Workflow
        description (Optional[str]): A rich description of the Workflow
    """

    display_name: str
    name: str
    summary: str
    contact_point_name: str
    contact_point_email: str

    publisher_id: Optional[str] = None
    description: Optional[str] = None
    licence: Optional[str] = None
    rights: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("summary", "summary", str),
        ParserParam("description", "description", str),
        ParserParam("publisher_id", "publisher", str),
        ParserParam("contact_point_name", "contact_point_name", str),
        ParserParam("contact_point_email", "contact_point_email", str),
        ParserParam("licence", "licence", str),
        ParserParam("rights", "rights", str),
    ]
