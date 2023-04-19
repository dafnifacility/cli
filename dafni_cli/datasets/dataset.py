from dataclasses import dataclass
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
        description (str): Description of the dataset
        formats (List[str]): The file formats related to the dataset
        modified_date (datetime): Date for when the dataset was last modified
        source (str): Publisher of the dataset e.g. DAFNI
        subject (str): Subject relating to the dataset e.g. Transportation
        title (str): Title of the dataset
        date_range_start (datetime or None): Start of date range
        date_range_end (datetime or None): End of date range
    """

    asset_id: str
    dataset_id: str
    version_id: str
    metadata_id: str
    description: str
    formats: List[str]
    modified_date: datetime
    source: str
    subject: str
    title: str
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("asset_id", ["id", "asset_id"], str),
        ParserParam("dataset_id", ["id", "dataset_uuid"], str),
        ParserParam("version_id", ["id", "version_uuid"], str),
        ParserParam("metadata_id", ["id", "metadata_uuid"], str),
        ParserParam("description", "description", str),
        ParserParam("formats", "formats"),
        ParserParam("modified_date", "modified_date", parse_datetime),
        ParserParam("source", "source", str),
        ParserParam("subject", "subject", str),
        ParserParam("title", "title", str),
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
        prose_print(self.description, CONSOLE_WIDTH)
        click.echo("")
