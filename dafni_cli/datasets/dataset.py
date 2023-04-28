from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, List, Optional

import click

from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.utils import prose_print


@dataclass
class Dataset(ParserBaseObject):
    """Dataclass representing a DAFNI dataset (As returned from the catalogue)

    Methods:
        output_dataset_details(): Prints key information of the dataset to console.

    Attributes:
        asset_id (str): Asset identifier for dataset
        dataset_id (str): Dataset identifier
        version_id (str): Version identifier of the latest version of this
                          dataset
        metadata_id (str): Metadata identifier of the latest metadata for this
                           dataset
        modified_date (datetime): Date for when the dataset was last modified
        source (str): Publisher of the dataset e.g. DAFNI
        subject (str): Subject relating to the dataset e.g. Transportation
        title (str): Title of the dataset
        formats (List[str]): The file formats related to the dataset
        description (Optional[str]): Description of the dataset
        date_range_start (Optional[datetime]): Start of date range
        date_range_end (Optional[datetime]): End of date range
    """

    asset_id: str
    dataset_id: str
    version_id: str
    metadata_id: str
    modified_date: datetime
    source: str
    subject: str
    title: str
    formats: List[str] = field(default_factory=list)
    description: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("asset_id", ["id", "asset_id"], str),
        ParserParam("dataset_id", ["id", "dataset_uuid"], str),
        ParserParam("version_id", ["id", "version_uuid"], str),
        ParserParam("metadata_id", ["id", "metadata_uuid"], str),
        ParserParam("modified_date", "modified_date", parse_datetime),
        ParserParam("source", "source", str),
        ParserParam("subject", "subject", str),
        ParserParam("title", "title", str),
        ParserParam("formats", "formats"),
        ParserParam("description", "description", str),
        ParserParam("date_range_start", ["date_range", "begin"], parse_datetime),
        ParserParam("date_range_end", ["date_range", "end"], parse_datetime),
    ]

    def output_dataset_details(self):
        """Prints relevant dataset attributes to command line"""
        click.echo("Title: " + self.title)
        click.echo("ID: " + self.dataset_id)
        click.echo("Latest Version: " + self.version_id)
        click.echo("Publisher: " + self.source)
        start = (
            self.date_range_start.date().strftime("%B %d %Y")
            if self.date_range_start
            else TAB_SPACE
        )
        end = (
            self.date_range_end.date().strftime("%B %d %Y")
            if self.date_range_end
            else TAB_SPACE
        )
        date_range_str = f"From: {start}{TAB_SPACE}To: {end}"
        click.echo(date_range_str)
        click.echo("Description: ")
        prose_print(self.description or "", CONSOLE_WIDTH)
        click.echo("")


# The following methods mostly exists to get round current python limitations
# with typing (see https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
def parse_datasets(dataset_dictionary_list: List[dict]) -> List[Dataset]:
    """Parses the output of get_all_datasets and returns a list of Dataset
    instances"""

    # "metadata" is used here as the endpoint get_all_datasets
    # actually used the catalogue endpoint where the search results are
    # under this key
    return ParserBaseObject.parse_from_dict_list(
        Dataset, dataset_dictionary_list["metadata"]
    )
