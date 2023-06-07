import copy
import json
import textwrap
from dataclasses import fields
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional, Tuple, Type, Union
from zipfile import ZipFile

import click
from tabulate import tabulate

from dafni_cli.consts import (
    DATE_INPUT_FORMAT,
    DATE_INPUT_FORMAT_VERBOSE,
    DATE_OUTPUT_FORMAT,
    DATE_TIME_OUTPUT_FORMAT,
    TABULATE_ARGS,
)


def prose_print(prose: str, width: int):
    """Prints string as separate paragraphs with appropriate line breaks at
    specified line lengths

    Args:
        prose (str): string to print as prose
        width (int): width of the lines before a new line
    """
    for paragraph in prose.split("\n"):
        for line in textwrap.wrap(paragraph, width=width):
            click.echo(line)


def optional_column(value: Optional[Any], column_width: int = 0, alignment: str = "<"):
    """Formats a value that may be None to have a specific width in a column

    When the value is None, will return a string with spaces of the desired
    width

    Args:
         value (Optional[Any]): Data that is to be checked and formatted if
                                not None
         column_width (int): Number of spaces to be returned instead if the
                             key is not present
         alignment (str): Specified alignment of column
    Returns:
        entry (str): Either the value of the entry to be put into the table,
                     column_width number of spaces

    Raises:
        ValueError - If the column_width is negative
    """
    if column_width < 0:
        raise ValueError("Column width for optional column must be non-negative")

    if value is not None:
        entry_string = str(value)
        if column_width > 0:
            entry = f"{entry_string:{alignment}{column_width}}"
        elif column_width == 0:
            entry = entry_string
    else:
        entry = " " * column_width
    return entry


def process_file_size(file_size: str) -> str:
    """Utility function to take in a file size in bytes
    and format into a table ready format.
    This converts the size into appropriate units, with
    the units appended

    Args:
        file_size (str): File size in bytes

    Returns:
        str: Converted file size with applicable units
    """
    try:
        file_size = float(file_size)
    except BaseException:
        return ""

    if file_size < 1e3:
        return f"{file_size} B"
    elif file_size >= 1e3 and file_size < 1e6:
        size = round(file_size / 1e3, 1)
        return f"{size} KB"
    elif file_size >= 1e6 and file_size < 1e9:
        size = round(file_size / 1e6, 1)
        return f"{size} MB"
    else:
        size = round(file_size / 1e9, 1)
        return f"{size} GB"


def argument_confirmation(
    arguments: List[Tuple[str, str]],
    confirmation_message: str,
    additional_messages: Optional[List[str]] = None,
):
    """Function to display the arguments and options chosen by the user
    and ask for confirmation

    Args:
        arguments (List[Tuple[str, str]]): Dictionary of the names and values
                               of the arguments/options for the command
        confirmation_message (str): String to display after arguments which
                                    prompts the user to confirm or reject
        additional_messages (Optional[List[str]]): Other messages to be added
                                    after options are listed
    """
    for name, value in arguments:
        click.echo(f"{name}: {value}")
    if additional_messages:
        for message in additional_messages:
            click.echo(message)
    click.confirm(confirmation_message, abort=True)


def write_files_to_zip(
    zip_path: Path, file_names: List[str], file_contents: List[BytesIO]
) -> None:
    """Function to compress a list of files to a zip folder, and write to disk

    Args:
        zip_path (Path): Full path including file name to write to
        file_names (List[str]): List of all file names
        file_contents (List[BytesIO]): List of file contents, 1 for each name
    """
    with ZipFile(zip_path, "w") as zipObj:
        for idx, file_name in enumerate(file_names):
            with zipObj.open(file_name, "w") as zip_file:
                zip_file.write(file_contents[idx].getvalue())


def print_json(response: Union[dict, List[dict]]) -> None:
    """Takes dictionary or list of dictionary and pretty prints to command line

    Args:
        response (Union[dict, List[dict]]): Dictionary or list of dictionaries to pretty print
    """
    click.echo(json.dumps(response, indent=2, sort_keys=True))


def dataclass_from_dict(class_type: Type, dictionary: dict):
    """Converts a dictionary of values into a particular dataclass type

    Args:
        class_type (Type): Class type to convert the dictionary to
        dictionary (dict): Dictionary containing the parameters needed for the
                           dataclass
    """

    field_set = {f.name for f in fields(class_type) if f.init}
    filtered_arg_dict = {k: v for k, v in dictionary.items() if k in field_set}
    return class_type(**filtered_arg_dict)


def format_table(
    headers: List[str],
    rows: List[List[Any]],
    max_column_widths: Optional[List[Optional[int]]] = None,
) -> str:
    """Returns a table using tabulate

    Can also wrap text within a column that exceeds a given maximum width.

    Args:
        headers (List[str]): List of headers of the table
        rows (List[List[str]]): List of rows in the table. Each row is a
                    list of values and there should be one for each header.
        max_column_widths (Optional[List[Optional[int]]]): List of maximum
                    widths for each column. When values are given for each
                    heading will automatically wrap the text onto a new line
                    within the column. (Useful for columns that may be
                    extremely long)
    """
    # Apply text wrapping if needed
    if max_column_widths:
        # Don't modify the rows passed in by accident
        rows = copy.deepcopy(rows)

        for row in rows:
            for value_idx, max_column_width in enumerate(max_column_widths):
                if max_column_width and row[value_idx]:
                    wrapped_values = textwrap.wrap(row[value_idx], max_column_width)
                    row[value_idx] = "\n".join(wrapped_values)

    return tabulate(rows, headers, **TABULATE_ARGS)


def format_datetime(value: Optional[datetime], include_time: bool) -> str:
    """Returns a string representation of a datetime object for output

    Will return 'N/A' if the datetime value given is None

    Args:
        value (datetime): Datetime value to format
        include_time: Whether to include the time in the returned string
    """
    if value:
        if include_time:
            return value.strftime(DATE_TIME_OUTPUT_FORMAT)
        else:
            return value.strftime(DATE_OUTPUT_FORMAT)
    return "N/A"
