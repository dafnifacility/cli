from dataclasses import dataclass
from typing import ClassVar, List, Optional

from dafni_cli.api.parser import ParserBaseObject, ParserParam
from dafni_cli.consts import (
    OUTPUT_FORMAT_COLUMN_WIDTH,
    OUTPUT_FORMAT_HEADER,
    OUTPUT_NAME_HEADER,
    OUTPUT_SUMMARY_COLUMN_WIDTH,
    OUTPUT_SUMMARY_HEADER,
)
from dafni_cli.utils import optional_column_new


@dataclass
class ModelOutputDataset(ParserBaseObject):
    """Dataclass containing information on an output dataset from a model

    Attributes:
        name (str): Name of the dataset output
        type (str): Type of the dataset output
        description (str): Description of the dataset output
    """

    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("type", "type", str),
        ParserParam("description", "description", str),
    ]


@dataclass
class ModelOutputs(ParserBaseObject):
    """Dataclass representing outputs for a DAFNI model

    Attributes:
        datasets (List[ModelOutputDataset]): List of output datasets
    """

    datasets: List[ModelOutputDataset]

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("datasets", "datasets", ModelOutputDataset),
    ]

    @staticmethod
    def outputs_table_header(name_column_width: int) -> str:
        """Formats the header row and the dashed line for the output parameters
           table

        Args:
            name_column_width (int): Width of the name column to fit the
                                     longest name (or "name") plus a buffer

        Returns:
            str: Formatted string for the header and dashed line of the outputs table
        """
        header = (
            f"{OUTPUT_NAME_HEADER:{name_column_width}}"
            f"{OUTPUT_FORMAT_HEADER:{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            f"{OUTPUT_SUMMARY_HEADER}\n"
            + "-"
            * (
                name_column_width
                + OUTPUT_FORMAT_COLUMN_WIDTH
                + OUTPUT_SUMMARY_COLUMN_WIDTH
            )
            + "\n"
        )
        return header

    def format_outputs(self) -> str:
        """Formats output files into a string which prints as a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """
        names = [dataset.name for dataset in self.datasets] + ["Name"]
        max_name_length = len(max(names, key=len)) + 2
        outputs_table = ModelOutputs.outputs_table_header(max_name_length)

        # The dataset outputs fields are not mandatory and any or all of them might not
        # exist. Unset fields will be reported as "Unknown" in the formatted output.
        for dataset in self.datasets:
            outputs_table += f"{dataset.name or 'Unknown':{max_name_length}}"
            outputs_table += f"{dataset.type or 'Unknown':{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            outputs_table += optional_column_new(dataset.description)
            outputs_table += "\n"
        return outputs_table
