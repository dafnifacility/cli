from dateutil.parser import isoparse
import click

from dafni_cli.consts import CONSOLE_WIDTH, DATA_FORMATS
from dafni_cli.utils import (
    check_key_in_dict,
    process_dict_datetime,
    prose_print,
    output_table_header,
    output_table_row,
    optional_column,
    process_file_size,
)


class DataFile:
    def __init__(self, file_dict: dict):
        self.name = check_key_in_dict(file_dict, "spdx:fileName")
        self.size = process_file_size(
            check_key_in_dict(file_dict, "dcat:byteSize", default=None)
        )
        self.format = DATA_FORMATS.get(
            check_key_in_dict(file_dict, "dcat:mediaType"), ""
        )


class DatasetMeta:
    def __init__(self):
        self.created = None
        self.creator = None
        self.contact = None
        self.description = None
        self.identifier = None
        self.location = None
        self.start_date = None
        self.end_date = None
        self.files = []
        self.keywords = []
        self.themes = None
        self.publisher = None
        self.issued = None
        self.rights = None
        self.language = None
        self.standard = None
        self.update = None

    def set_details_from_dict(self, dataset_dict: dict):
        # Standard Metadata
        self.created = process_dict_datetime(dataset_dict, "dct:created")
        self.creator = check_key_in_dict(dataset_dict, "dct:creator", "foaf:name")
        self.contact = check_key_in_dict(
            dataset_dict, "dcat:contactPoint", "vcard:hasEmail"
        )
        self.description = check_key_in_dict(dataset_dict, "dct:description")
        self.identifier = check_key_in_dict(dataset_dict, "dct:identifier")
        self.location = check_key_in_dict(dataset_dict, "dct:spatial", "rdfs:label")
        self.start_date = process_dict_datetime(
            dataset_dict, "dct:PeriodOfTime", "time:hasBeginning"
        )
        self.end_date = process_dict_datetime(
            dataset_dict, "dct:PeriodOfTime", "time:hasEnd"
        )
        self.keywords = check_key_in_dict(dataset_dict, "dcat:keyword")

        # Process Files
        if check_key_in_dict(dataset_dict, "dcat:distribution", default=None):
            self.files = [
                DataFile(file_dict) for file_dict in dataset_dict["dcat:distribution"]
            ]

        # Additional Metadata fields
        self.themes = check_key_in_dict(dataset_dict, "dcat:theme")
        self.publisher = check_key_in_dict(dataset_dict, "dct:publisher", "foaf:name")
        self.issued = process_dict_datetime(dataset_dict, "dct:issued")
        self.rights = check_key_in_dict(dataset_dict, "dct:rights")
        self.language = check_key_in_dict(dataset_dict, "dct:language")
        self.standard = check_key_in_dict(dataset_dict, "dct:conformsTo", "label")
        self.update = check_key_in_dict(dataset_dict, "dct:accrualPeriodicity")

    def output_metadata_details(self, long: bool = False):
        click.echo(f"\nCreated: {self.created}")
        click.echo(f"Creator: {self.creator}")
        click.echo(f"Contact: {self.contact}")
        click.echo("Description:")
        prose_print(self.description, CONSOLE_WIDTH)
        click.echo("Identifier: ")
        prose_print(" ".join(self.identifier), CONSOLE_WIDTH)
        click.echo(f"Location: {self.location}")
        click.echo(f"Start date: {self.start_date}")
        click.echo(f"End date: {self.end_date}")

        # DataFiles table
        self.output_datafiles_table()

        if long:
            self.output_metadata_extra_details()

    def output_datafiles_table(self):
        click.echo("\nData Files")

        columns = ["Name", "Size", "Format"]
        name_width = max([len(datafile.name) for datafile in self.files])
        widths = [name_width, 10, 10]

        table_data = output_table_header(columns, widths)
        table_data += "".join(
            [
                output_table_row(
                    [datafile.name, datafile.size, datafile.format], widths
                )
                for datafile in self.files
            ]
        )

        click.echo(table_data)

    def output_metadata_extra_details(self):
        click.echo(f"Themes: {self.themes}")
        click.echo(f"Publisher: {self.publisher}")
        click.echo(f"Issued: {self.issued}")
        click.echo("Rights:")
        prose_print(self.rights, CONSOLE_WIDTH)
        click.echo(f"Language: {self.language}")
        click.echo(f"Standard: {self.standard}")
        click.echo(f"Update Frequency: {self.update}")
