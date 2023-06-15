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

    if title:
        args.extend(["--title", title])
    if description:
        args.extend(["--description", description])
    if identifiers:
        for identifier in identifiers:
            args.extend(["--identifier", identifier])
    if subject:
        args.extend(
            [
                "--subject",
                subject,
            ]
        )
    if themes:
        for theme in themes:
            args.extend(["--theme", theme])
        args.extend(
            [
                "--language",
                language,
            ]
        )
    if language:
        args.extend(["--language", language])
    if keywords:
        for keyword in keywords:
            args.extend(["--keyword", keyword])
    if standard:
        args.extend(
            [
                "--standard",
                standard[0],
                standard[1],
            ]
        )
    if start_date:
        args.extend(["--start-date", start_date.strftime(DATE_INPUT_FORMAT)])
    if end_date:
        args.extend(["--end-date", end_date.strftime(DATE_INPUT_FORMAT)])
    if organisation:
        args.extend(
            [
                "--organisation",
                organisation[0],
                organisation[1],
            ]
        )
    if people:
        for person in people:
            args.extend(["--person", person[0], person[1]])
    # Special case - cant easily mock datetime.now so use ANY here instead
    if created_date:
        args.extend(
            [
                "--created-date",
                created_date.strftime(DATE_INPUT_FORMAT),
            ]
        )
    else:
        dictionary["created_date"] = ANY

    if update_frequency:
        args.extend(
            [
                "--update-frequency",
                update_frequency,
            ]
        )
    if publisher:
        args.extend(
            [
                "--publisher",
                publisher[0],
                publisher[1],
            ]
        )
    if contact:
        args.extend(
            [
                "--contact",
                contact[0],
                contact[1],
            ]
        )
    if license:
        args.extend(
            [
                "--license",
                license,
            ]
        )
    elif not all_optional:
        dictionary["license"] = "https://creativecommons.org/licences/by/4.0/"

    if rights:
        args.extend(
            [
                "--rights",
                rights,
            ]
        )
    if version_message:
        args.extend(["--version-message", version_message])

    return args
