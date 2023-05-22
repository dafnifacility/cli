from dataclasses import dataclass
from typing import ClassVar, List, Optional

from dafni_cli.api.parser import ParserBaseObject, ParserParam
from dafni_cli.consts import (
    OUTPUT_FORMAT_HEADER,
    OUTPUT_NAME_HEADER,
    OUTPUT_SUMMARY_HEADER,
    OUTPUT_SUMMARY_MAX_COLUMN_WIDTH,
)
from dafni_cli.utils import format_table


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

    def format_outputs(self) -> str:
        """Formats output files into a string which prints as a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """

        # The dataset outputs fields are not mandatory and any or all of them might not
        # exist. Unset fields will be reported as "Unknown" in the formatted output.
        return format_table(
            headers=[
                OUTPUT_NAME_HEADER,
                OUTPUT_FORMAT_HEADER,
                OUTPUT_SUMMARY_HEADER,
            ],
            rows=[
                [
                    dataset.name or "Unknown",
                    dataset.type or "Unknown",
                    dataset.description,
                ]
                for dataset in self.datasets
            ],
            max_column_widths=[None, None, OUTPUT_SUMMARY_MAX_COLUMN_WIDTH],
        )
