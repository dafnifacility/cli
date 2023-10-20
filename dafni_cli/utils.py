import copy
import json
import re
import textwrap
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple, Type, Union
from urllib.parse import urlparse

import click
from tabulate import tabulate
from tqdm import tqdm

from dafni_cli.consts import (
    DATA_FORMATS,
    DATE_OUTPUT_FORMAT,
    DATE_TIME_OUTPUT_FORMAT,
    OUTPUT_UNKNOWN_FORMAT,
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


def format_file_size(file_size: str) -> str:
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
    skip: bool = False,
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
        skip (bool): Whether to skip the confirmation or not. A value of True
                     skips the entire confirmation, whereas False will request
                     input from the user after printing out any given messages
    """
    if not skip:
        for name, value in arguments:
            click.echo(f"{name}: {value}")
        if additional_messages:
            for message in additional_messages:
                click.echo(message)
        click.confirm(confirmation_message, abort=True)


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


def is_valid_url(value: str) -> bool:
    """Returns whether a string constitutes a valid URL

    Args:
        value (str): The string to check

    Returns:
        bool: Whether the string is a valid URL
    """
    try:
        parsed_url = urlparse(value)
        return all([parsed_url.scheme, parsed_url.netloc])
    except ValueError:
        return False


def is_valid_email_address(value: str) -> bool:
    """Returns whether a string constitutes a valid email address

    Args:
        value (str): The string to check

    Returns:
        bool: Whether the string is a valid email address
    """

    # Checks there is exactly one @ sign, and at least one . after it
    return re.match(r"[^@]+@[^@]+\.[^@]+", value)


def format_data_format(value: Optional[str]):
    """Converts a data format to a printable string"""
    if value is None:
        return OUTPUT_UNKNOWN_FORMAT
    return DATA_FORMATS.get(value, OUTPUT_UNKNOWN_FORMAT)


def construct_validation_errors_from_dict(dictionary: dict, prefix="") -> List[str]:
    """Convert a validation error dictionary into a list of errors

    e.g.
    {
        "metadata": {
            "description": [
                "This field is required."
            ]
        }
    }

    becomes

    [ "Error: ( metadata -> description ) - This field is required" ]
    """
    errors = []
    for key, value in dictionary.items():
        new_prefix = key
        if prefix != "":
            new_prefix = f"{prefix} -> {key}"

        if isinstance(value, dict):
            errors.extend(
                construct_validation_errors_from_dict(value, prefix=new_prefix)
            )
        elif isinstance(value, list):
            errors.append(f"Error: ( {new_prefix} ) - {value[0]}")
        else:
            errors.append(f"Error: ( {new_prefix} ) - {value}")
    return errors


def optional_echo(string: str, should_not_print: bool):
    """Uses click.echo to output a string only when should_not_print is False
    (Used for optional printing for json flags)"""
    if not should_not_print:
        click.echo(string)


def create_file_progress_bar(description: str, total: int, disable: bool = False):
    """Creates a progress bar intended for file operations

    Args:
        description (str): Description to print just before the bar (usually
                           file name)
        total (int): Total file size
        disable (bool): 'disable' parameter to pass through to tqdm
    """
    return tqdm(
        desc=description,
        total=total,
        miniters=1,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        disable=disable,
    )


class OverallFileProgressBar:
    """A progress bar that displays an overall status of an operation involving
    multiple files"""

    def __init__(self, total_files: int, total_size: int, disable: bool = False):
        """
        Args:
            total_files (int): Total number of files involved in the operation
            total_size (int): Total sum of all the file sizes
            disable (bool): disable value to pass to tqdm
        """
        self._total_files = total_files
        self._total_size = total_size
        self._disable = disable
        self._current_file = 0
        self._progress_bar = None

    def _get_description(self):
        return f"Overall progress {self._current_file}/{self._total_files}"

    def __enter__(self):
        self._progress_bar = create_file_progress_bar(
            description=self._get_description(),
            total=self._total_size,
            disable=self._disable,
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._progress_bar.close()

    def update(self, file_size: int):
        """Should be called after an operation on a file has completed, will then
        update the status of the loading bar

        Args:
            file_size (int): Size of the file that just finished uploading"""
        self._current_file += 1
        self._progress_bar.set_description(self._get_description())
        self._progress_bar.update(file_size)


def is_valid_definition_file(file_name: Path):
    """Takes file name and gets the file type.
    Returns true if file type is in list of '.json', '.yml' or '.yaml'.

    Args:
        file_name (Path): the full name of the file including the file type.

    Returns:
        bool: Whether or not the file type is valid.

    """
    try:
        valid_file_types = ("yml", "yaml", "json")
        file_type = str(file_name).split(".")[1]
        return file_type in valid_file_types
    except:
        return False


def is_valid_image_file(file_name: Path):
    """Returns whether a file name contains the valid file type for docker image

    Args:
        file_name (Path): name of file to be checked

    Returns:
        bool: Whether the file type is valid
    """
    try:
        acceptable_file_types = ["tar", "tar.gz"]
        file_name = str(file_name)
        file_type = file_name.split(".", 1)[1]
        return file_type in acceptable_file_types
    except:
        return False


def split_list(lst: List, max_size: int):
    """Splits a given list into 'max_size' or smaller lists

    Args:
        lst (List): List to split
        max_size: Maximum size of any given list returned

    Returns:
        Generator[List]: A generator that returns a list with a maximum
                         size max_size e.g. use list(list_split(lst, max_size))

    """
    for i in range(0, len(lst), max_size):
        yield lst[i : i + max_size]


def get_current_messages(all_notifications: List[dict]) -> List[str]:
    """Gets the currently active messages from list of notification

    Args:
        all_notifications (List): List of notifications

    Returns:
        current_messages[List]: List of active messages

    """
    now = datetime.now()
    current_messages = [
        notification["message"]
        for notification in all_notifications
        if notification["start_date"] < now and notification["end_date"] > now
    ]
    return current_messages
