from dataclasses import dataclass, field
from typing import Any, ClassVar, List, Optional

from dafni_cli.api.parser import ParserBaseObject, ParserParam
from dafni_cli.consts import (
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_DESCRIPTION_MAX_COLUMN_WIDTH,
    INPUT_MAX_HEADER,
    INPUT_MIN_HEADER,
    INPUT_TITLE_HEADER,
    INPUT_TYPE_HEADER,
    TAB_SPACE,
)
from dafni_cli.utils import format_table


@dataclass
class ModelDataslot(ParserBaseObject):
    """Dataclass representing an input dataslot for a DAFNI
       model

    Attributes:
        name (str): Name of the slot
        path (str): Path of the file expected in the container
        defaults (List[str]): List of default dataset ids
        required (str): Whether the slot is required
        description (Optional[str]): Description of the slot if applicable
    """

    name: str
    path: str
    defaults: List[str]
    required: bool
    description: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("path", "path", str),
        ParserParam("defaults", "default"),
        ParserParam("required", "required"),
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
                INPUT_TYPE_HEADER,
                INPUT_MIN_HEADER,
                INPUT_MAX_HEADER,
                INPUT_DEFAULT_HEADER,
                INPUT_DESCRIPTION_HEADER,
            ],
            rows=[
                [
                    parameter.title,
                    parameter.type,
                    parameter.min,
                    parameter.max,
                    parameter.default,
                    parameter.description,
                ]
                for parameter in self.parameters
            ],
            max_column_widths=[
                None,
                None,
                None,
                None,
                None,
                INPUT_DESCRIPTION_MAX_COLUMN_WIDTH,
            ],
        )

    def format_dataslots(self) -> Optional[str]:
        """Formats input data slots to print in a clear way

        Returns:
            Optional[str]: Formatted string that will present the dataslots
                           clearly when printed
        """

        if self.dataslots:
            dataslots_list = ""
            for dataslot in self.dataslots:
                dataslots_list += "Name: " + dataslot.name + "\n"
                dataslots_list += "Path in container: " + dataslot.path + "\n"
                dataslots_list += f"Required: {dataslot.required}\n"
                dataslots_list += "Default Datasets: \n"
                for default_val in dataslot.defaults:
                    # TODO print name using API call to databases
                    dataslots_list += "ID: " + default_val + TAB_SPACE
                    # dataslots_list += f'ID: {default["uid"]}' + TAB_SPACE
                    # dataslots_list += f'Version ID: {default["versionUid"]}' + TAB_SPACE
                dataslots_list += "\n"
            return dataslots_list
        return None
