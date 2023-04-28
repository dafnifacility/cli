from dataclasses import dataclass, field
from typing import Any, ClassVar, List, Optional

from dafni_cli.api.parser import ParserBaseObject, ParserParam
from dafni_cli.consts import (
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_DESCRIPTION_LINE_WIDTH,
    INPUT_MAX_HEADER,
    INPUT_MIN_HEADER,
    INPUT_MIN_MAX_COLUMN_WIDTH,
    INPUT_TITLE_HEADER,
    INPUT_TYPE_COLUMN_WIDTH,
    INPUT_TYPE_HEADER,
    TAB_SPACE,
)
from dafni_cli.utils import optional_column


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

    # TODO: Couldn't we use tabulate or something for this?
    @staticmethod
    def params_table_header(title_column_width: int, default_column_width: int) -> str:
        """Formats the header row and the dashed line for an input parameters
           table

        Args:
            title_column_width (int): Width of the title column to fit the
                                      longest title (or "title") plus a buffer
            default_column_width (int): Width of the default column to fit the
                                        longest default (or "default") plus a
                                        buffer

        Returns:
            str: Formatted string for the header and dashed line of the
                 parameters table
        """

        header = (
            f"{INPUT_TITLE_HEADER:{title_column_width}}"
            f"{INPUT_TYPE_HEADER:{INPUT_TYPE_COLUMN_WIDTH}}"
            f"{INPUT_MIN_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
            f"{INPUT_MAX_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
            f"{INPUT_DEFAULT_HEADER:{default_column_width}}"
            f"{INPUT_DESCRIPTION_HEADER}\n"
            + "-"
            * (
                title_column_width
                + INPUT_TYPE_COLUMN_WIDTH
                + 2 * INPUT_MIN_MAX_COLUMN_WIDTH
                + default_column_width
                + INPUT_DESCRIPTION_LINE_WIDTH
            )
            + "\n"
        )
        return header

    def format_parameters(self) -> str:
        """Formats input parameters for a model into a string which prints as
           a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """

        titles = [parameter.title for parameter in self.parameters] + ["title"]
        defaults = ["default"]
        for parameter in self.parameters:
            if parameter.default is not None:
                defaults.append(str(parameter.default))
        title_column_width = len(max(titles, key=len)) + 2
        default_column_width = len(max(defaults, key=len)) + 2
        # Setup headers
        params_table = ModelInputs.params_table_header(
            title_column_width, default_column_width
        )
        # Populate table
        for parameter in self.parameters:
            params_table += f"{parameter.title:{title_column_width}}{parameter.type:{INPUT_TYPE_COLUMN_WIDTH}}"
            params_table += optional_column(parameter.min, INPUT_MIN_MAX_COLUMN_WIDTH)
            params_table += optional_column(parameter.max, INPUT_MIN_MAX_COLUMN_WIDTH)
            params_table += optional_column(parameter.default, default_column_width)
            params_table += f"{parameter.description}\n"
        return params_table

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
