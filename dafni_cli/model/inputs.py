from dataclasses import dataclass, field
from typing import Any, ClassVar, List, Optional

from dafni_cli.api.parser import ParserBaseObject, ParserParam
from dafni_cli.consts import (
    INPUT_DEFAULT_DATASETS_HEADER,
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_DESCRIPTION_MAX_COLUMN_WIDTH,
    INPUT_MAX_HEADER,
    INPUT_MIN_HEADER,
    INPUT_NAME_HEADER,
    INPUT_PATH_IN_CONTAINER_HEADER,
    INPUT_REQUIRED_HEADER,
    INPUT_TITLE_HEADER,
    INPUT_TYPE_HEADER,
)
from dafni_cli.utils import format_table


@dataclass
class ModelDataslot(ParserBaseObject):
    """Dataclass representing an input dataslot for a DAFNI
       model

    Attributes:
        name (str): Name of the slot
        path (str): Path of the file expected in the container
        required (str): Whether the slot is required
        defaults (List[str]): List of default dataset ids
        description (Optional[str]): Description of the slot if applicable
    """

    name: str
    path: str
    required: bool
    defaults: List[str] = field(default_factory=list)
    description: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("path", "path", str),
        ParserParam("required", "required"),
        ParserParam("defaults", "default"),
        ParserParam("description", "description", str),
    ]


@dataclass
class ModelParameter(ParserBaseObject):
    """Dataclass representing an input parameter for a DAFNI model

    Attributes:
        name (str): Name of the parameter
        type (str): Type of the parameter
        title(str): Title of the parameter
        required (bool): Whether the parameter is required
        description (str): Description of the model parameter
        default (Optional[Any]): Default value of the parameter
        min (Optional[str]): Minimum value of a numeric parameter (if any)
        max (Optional[str]): Maximum value of a numeric parameter (if any)
    """

    name: str
    type: str
    title: str
    required: bool
    description: str
    default: Optional[Any] = None
    min: Optional[str] = None
    max: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("type", "type", str),
        ParserParam("title", "title"),
        ParserParam("required", "required"),
        ParserParam("description", "description"),
        ParserParam("default", "default"),
        ParserParam("min", "min"),
        ParserParam("max", "max"),
    ]


@dataclass
class ModelInputs(ParserBaseObject):
    """Dataclass representing inputs for a DAFNI model

    Attributes:
        parameters (List[ModelParameters]): List of parameters for the model
        dataslots (List[ModelDataslot]): List of dataslots for the model
    """

    parameters: List[ModelParameter]
    dataslots: List[ModelDataslot] = field(default_factory=list)

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("parameters", "parameters", ModelParameter),
        ParserParam("dataslots", "dataslots", ModelDataslot),
    ]

    def format_parameters(self) -> str:
        """Formats input parameters for a model into a string which prints as
           a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """
        return format_table(
            headers=[
                INPUT_TITLE_HEADER,
                INPUT_DESCRIPTION_HEADER,
                INPUT_NAME_HEADER,
                INPUT_TYPE_HEADER,
                INPUT_MIN_HEADER,
                INPUT_MAX_HEADER,
                INPUT_DEFAULT_HEADER,
                INPUT_REQUIRED_HEADER,
            ],
            rows=[
                [
                    parameter.title,
                    parameter.description,
                    parameter.name,
                    parameter.type,
                    parameter.min,
                    parameter.max,
                    parameter.default,
                    "Yes" if parameter.required else "No",
                ]
                for parameter in self.parameters
            ],
            max_column_widths=[
                None,
                INPUT_DESCRIPTION_MAX_COLUMN_WIDTH,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        )

    def format_dataslots(self) -> Optional[str]:
        """Formats input data slots for a model into a string which prints as
           a table

        Returns:
            Optional[str]: str: Formatted string that will appear as a table
                                when printed
        """

        if self.dataslots:
            return format_table(
                headers=[
                    INPUT_TITLE_HEADER,
                    INPUT_DESCRIPTION_HEADER,
                    INPUT_PATH_IN_CONTAINER_HEADER,
                    INPUT_DEFAULT_DATASETS_HEADER,
                    INPUT_REQUIRED_HEADER,
                ],
                rows=[
                    [
                        dataslot.name,
                        dataslot.description,
                        dataslot.path,
                        "\n".join(dataslot.defaults),
                        "Yes" if dataslot.required else "No",
                    ]
                    for dataslot in self.dataslots
                ],
                max_column_widths=[
                    None,
                    INPUT_DESCRIPTION_MAX_COLUMN_WIDTH,
                    None,
                    None,
                    None,
                ],
            )
        return None
