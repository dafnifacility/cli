from datetime import datetime
from typing import List, Optional, Tuple
from unittest.mock import ANY

from dafni_cli.consts import DATE_INPUT_FORMAT


def add_dataset_metadata_common_options(
    args: List[str],
    all_optional: bool,
    dictionary: dict,
    title: Optional[str],
    description: Optional[str],
    identifiers: Optional[Tuple[str]],
    subject: Optional[str],
    themes: Optional[Tuple[str]],
    language: Optional[str],
    keywords: Optional[Tuple[str]],
    standard: Optional[Tuple[str, str]],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    organisation: Optional[Tuple[str, str]],
    people: Optional[Tuple[Tuple[str, str]]],
    created_date: Optional[datetime],
    update_frequency: Optional[str],
    publisher: Optional[Tuple[str, str]],
    contact: Optional[Tuple[str]],
    license: Optional[str],
    rights: Optional[str],
    version_message: Optional[str],
):
    """Adds command line arguments to match the options added by the
    dataset_metadata_common_options decorator

    This also returns a modified dictionary of values representing the
    expected values (in case their defaults are different)

    Args:
        args (List[str]): List of arguments being input
        all_optional (bool): Should be the same as what is passed to the
                             dataset_metadata_common_options decorator - used
                             to set the correct default values
        dictionary (dict): Used to pass in the parameters - modified to match
                           expected values passed through click including any
                           default parameters

        See dataset_metadata_common_options for all of the actual options
    """

    if title is not None:
        args.extend(["--title", title])
    if description is not None:
        args.extend(["--description", description])
    if identifiers is not None:
        for identifier in identifiers:
            args.extend(["--identifier", identifier])
    if subject is not None:
        args.extend(
            [
                "--subject",
                subject,
            ]
        )
    if themes is not None:
        for theme in themes:
            args.extend(["--theme", theme])
        args.extend(
            [
                "--language",
                language,
            ]
        )
    if language is not None:
        args.extend(["--language", language])
    if keywords is not None:
        for keyword in keywords:
            args.extend(["--keyword", keyword])
    if standard is not None:
        args.extend(
            [
                "--standard",
                standard[0],
                standard[1],
            ]
        )
    if start_date is not None:
        args.extend(["--start-date", start_date.strftime(DATE_INPUT_FORMAT)])
    if end_date is not None:
        args.extend(["--end-date", end_date.strftime(DATE_INPUT_FORMAT)])
    if organisation is not None:
        args.extend(
            [
                "--organisation",
                organisation[0],
                organisation[1],
            ]
        )
    if people is not None:
        for person in people:
            args.extend(["--person", person[0], person[1]])
    # Special case - cant easily mock datetime.now so use ANY here instead
    if created_date is not None:
        args.extend(
            [
                "--created-date",
                created_date.strftime(DATE_INPUT_FORMAT),
            ]
        )
    else:
        dictionary["created_date"] = ANY

    if update_frequency is not None:
        args.extend(
            [
                "--update-frequency",
                update_frequency,
            ]
        )
    if publisher is not None:
        args.extend(
            [
                "--publisher",
                publisher[0],
                publisher[1],
            ]
        )
    if contact is not None:
        args.extend(
            [
                "--contact",
                contact[0],
                contact[1],
            ]
        )
    if license is not None:
        args.extend(
            [
                "--license",
                license,
            ]
        )
    elif not all_optional:
        dictionary["license"] = "https://creativecommons.org/licenses/by/4.0/"

    if rights is not None:
        args.extend(
            [
                "--rights",
                rights,
            ]
        )
    if version_message is not None:
        args.extend(["--version-message", version_message])

    return args
