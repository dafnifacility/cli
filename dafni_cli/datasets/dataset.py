from dateutil import parser
import click
from typing import List

from dafni_cli.consts import TAB_SPACE, CONSOLE_WIDTH
from dafni_cli.model import prose_print


class Permissions:
    def __init__(self, permissions: dict):
        self.name = permissions["name"]
        self.view = permissions["view"]
        self.read = permissions["read"]
        self.update = permissions["update"]
        self.destroy = permissions["destroy"]
        self.reason = permissions["reason"]


class Dataset:
    def __init__(self):
        self.id = None
        self.version_id = None
        self.metadata_id = None
        self.asset_id = None
        self.title = None
        self.description = None
        self.subject = None
        self.source = None
        self.date_range_start = None
        self.date_range_end = None
        self.modified = None
        self.formats = None

    def set_details_from_dict(self, dataset: dict):
        self.id = dataset["id"]["dataset_uuid"]
        self.version_id = dataset["id"]["version_uuid"]
        self.metadata_id = dataset["id"]["metadata_uuid"]
        self.asset_id = dataset["id"]["asset_id"]
        self.title = dataset["title"]
        self.description = dataset["description"]
        self.subject = dataset["subject"]
        self.source = dataset["source"]
        if dataset["date_range"]["begin"]:
            self.date_range_start = parser.isoparse(dataset["date_range"]["begin"])
        if dataset["date_range"]["end"]:
            self.date_range_end = parser.isoparse(dataset["date_range"]["end"])
        self.modified = dataset["modified_date"]
        self.formats = dataset["formats"]
        self.permissions = Permissions(dataset["auth"])

    def output_dataset_details(self):
        """Prints relevant dataset attributes to command line"""
        click.echo("Title: " + self.title)
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
