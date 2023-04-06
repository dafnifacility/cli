from dateutil import parser
import click
from typing import List

from dafni_cli.consts import TAB_SPACE, CONSOLE_WIDTH
from dafni_cli.utils import prose_print


class Dataset:
    """Class to represent the DAFNI Dataset
    client model

    Methods:
        __init__(): Dataset constructor
        set_attributes_from_dict(jwt (str), dataset (dict)): Sets the dataset attributes from given client model dict
        output_dataset_details(): Prints key information of the dataset to console.

    Attributes:
        asset_id: Asset identifier
        date_range_end: End of date range
        date_range_start: Start of date range
        description: Description of the dataset
        formats: The file formats related to the dataset
        id: Dataset identifier
        metadata_id: Meta data identifier
        modified: Date for when the dataset was last modified
        source: Publisher of the dataset e.g. DAFNI
        subject: Subject relating to the dataset e.g. Transportation
        title: Title of the dataset
        version_id: Version identifier for the latest version of the dataset
    """

    def __init__(self):
        """Dataset constructor"""
        self.asset_id = None
        self.date_range_end = None
        self.date_range_start = None
        self.description = None
        self.formats = None
        self.id = None
        self.metadata_id = None
        self.modified = None
        self.source = None
        self.subject = None
        self.title = None
        self.version_id = None

    def set_attributes_from_dict(self, dataset: dict):
        """Helper function to populate the Dataset attributes
        based on a given DAFNI Dataset client model

        Args:
            dataset (dict): DAFNI Dataset client model
        """
        self.asset_id = dataset["id"]["asset_id"]
        self.description = dataset["description"]
        self.formats = dataset["formats"]
        self.id = dataset["id"]["dataset_uuid"]
        self.metadata_id = dataset["id"]["metadata_uuid"]
        self.modified = dataset["modified_date"]
        self.source = dataset["source"]
        self.subject = dataset["subject"]
        self.title = dataset["title"]
        self.version_id = dataset["id"]["version_uuid"]
        # DateRanges
        if dataset["date_range"]["begin"]:
            self.date_range_start = parser.isoparse(dataset["date_range"]["begin"])
        if dataset["date_range"]["end"]:
            self.date_range_end = parser.isoparse(dataset["date_range"]["end"])

    def output_dataset_details(self):
        """Prints relevant dataset attributes to command line"""
        click.echo("Title: " + self.title)
        click.echo("ID: " + self.id)
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
        date_range_str = "From: {0}{1}To: {2}".format(start, TAB_SPACE, end)
        click.echo(date_range_str)
        click.echo("Description: ")
        prose_print(self.description, CONSOLE_WIDTH)
        click.echo("")
