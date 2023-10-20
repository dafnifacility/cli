from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from freezegun import freeze_time

from dafni_cli import utils
from dafni_cli.consts import (
    DATA_FORMATS,
    DATE_OUTPUT_FORMAT,
    DATE_TIME_OUTPUT_FORMAT,
    OUTPUT_UNKNOWN_FORMAT,
    TABULATE_ARGS,
)


@patch("dafni_cli.utils.click")
class TestProsePrint(TestCase):
    """Test class to test the 'prose_print' function"""

    def test_string_shorter_than_width_prints_as_one_string(self, mock_click):
        """Test that a string shorter than the given width prints in one line"""

        # SETUP
        string = "123456"

        # CALL
        utils.prose_print(string, 10)

        # ASSERT
        mock_click.echo.assert_called_with(string)

    def test_string_without_line_breaks_or_spaces_is_split_correctly_and_printed_sequentially(
        self, mock_click
    ):
        """Test that a string longer than the given width prints in separate
        lines"""

        # SETUP
        string = "123456"

        # CALL
        utils.prose_print(string, 2)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call("12"),
                call("34"),
                call("56"),
            ]
        )

    def test_string_with_space_before_width_but_no_line_break_splits_at_space(
        self, mock_click
    ):
        """Test that a string longer than the given width prints in separate
        lines but split at a space in string"""

        # SETUP
        string = "12 3456"

        # CALL
        utils.prose_print(string, 4)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call("12"),
                call("3456"),
            ]
        )

    def test_string_with_line_break_splits_at_line_break(self, mock_click):
        """Test that a string longer than the given width prints in separate
        lines including while including a line break in string"""

        # SETUP
        string = "123456\n78"

        # CALL
        utils.prose_print(string, 4)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call("1234"),
                call("56"),
                call("78"),
            ]
        )


class TestFormatFileSize(TestCase):
    """Test class to test the format_file_size functionality"""

    def test_empty_string_returned_if_non_integer_or_float_value_given(self):
        """Tests that an empty string is returned if the given file size is
        an invalid type"""

        # SETUP
        values = [[12], (12, 13)]

        # CALL & ASSERT
        for file_size in values:
            self.assertEqual(utils.format_file_size(file_size), "")

    def test_file_size_processed_correctly(self):
        """Tests that the correct string is returned for various valid file
        sizes"""

        # SETUP
        values_and_results = [
            (1.0, "1.0 B"),
            (10.0, "10.0 B"),
            (100.0, "100.0 B"),
            (1e3, "1.0 KB"),
            (1e4, "10.0 KB"),
            (1e5, "100.0 KB"),
            (1e6, "1.0 MB"),
            (1e7, "10.0 MB"),
            (1e8, "100.0 MB"),
            (1e9, "1.0 GB"),
            (1e10, "10.0 GB"),
            (1e11, "100.0 GB"),
            (1e12, "1000.0 GB"),
            (1.5e3, "1.5 KB"),
            (2.7e6, "2.7 MB"),
            (3.8e9, "3.8 GB"),
            (2.743e6, "2.7 MB"),
            (3.854e9, "3.9 GB"),
        ]

        # CALL & ASSERT
        for file_size, result in values_and_results:
            self.assertEqual(utils.format_file_size(file_size), result)


@patch("dafni_cli.utils.click")
class TestArgumentConfirmation(TestCase):
    """Test class to test the argument_confirmation function"""

    def test_arguments_are_printed_correctly_without_additional_messages(
        self, mock_click
    ):
        """Tests that the arguments are printed correctly and the right calls
        are made to click"""
        # SETUP
        arguments = [
            ("arg 1", "string option"),
            ("arg 2", "12"),
            ("arg 3", "{'key': 'value'}"),
        ]
        confirmation_message = "confirmation message"

        # CALL
        utils.argument_confirmation(arguments, confirmation_message)

        # ASSERT
        self.assertEqual(
            mock_click.echo.call_args_list,
            [
                call("arg 1: string option"),
                call("arg 2: 12"),
                call("arg 3: {'key': 'value'}"),
            ],
        )
        mock_click.confirm.assert_called_once_with(confirmation_message, abort=True)

    def test_arguments_are_printed_correctly_with_additional_messages(self, mock_click):
        """Tests that the arguments are printed correctly and the right calls
        are made to click when additional messages are given"""
        # SETUP
        arguments = [
            ("arg 1", "string option"),
            ("arg 2", "12"),
            ("arg 3", "{'key': 'value'}"),
        ]
        confirmation_message = "confirmation message"
        additional_messages = ["additional message 1", "additional message 2"]

        # CALL
        utils.argument_confirmation(
            arguments, confirmation_message, additional_messages
        )

        # ASSERT
        self.assertEqual(
            mock_click.echo.call_args_list,
            [
                call("arg 1: string option"),
                call("arg 2: 12"),
                call("arg 3: {'key': 'value'}"),
                call("additional message 1"),
                call("additional message 2"),
            ],
        )
        mock_click.confirm.assert_called_once_with(confirmation_message, abort=True)

    def test_nothing_happens_when_skip_is_true(self, mock_click):
        """Tests that nothing is done when 'skip' is True"""
        # CALL
        utils.argument_confirmation(
            [
                ("arg 1", "string option"),
                ("arg 2", "12"),
                ("arg 3", "{'key': 'value'}"),
            ],
            "confirmation message",
            ["additional message 1", "additional message 2"],
            skip=True,
        )

        # ASSERT
        mock_click.echo.assert_not_called()
        mock_click.confirm.assert_not_called()


@patch("dafni_cli.utils.click")
@patch("dafni_cli.utils.json")
class TestPrintJSON(TestCase):
    """Test class to test the print_json function"""

    def test_print_json(self, mock_json, mock_click):
        """Tests print_json functions as expected"""
        # SETUP
        data = {"some": "test", "data": {"hello": 30}}

        # CALL
        utils.print_json(data)

        # ASSERT
        mock_json.dumps.assert_called_once_with(data, indent=2, sort_keys=True)
        mock_click.echo.assert_called_once_with(mock_json.dumps.return_value)


class TestDataclassFromDict(TestCase):
    """Test class to test the dataclass_from_dict function"""

    @dataclass
    class TestDataclass:
        name: str
        number: int
        list_of_values: List[str]
        optional: Optional[str] = None

    def test_dataclass_from_dict(self):
        """Tests dataclass_from_dict functions as expected"""

        # SETUP
        data = {
            "name": "test",
            "number": 10,
            "list_of_values": ["value1", "value2"],
            "optional": "some value",
        }

        # CALL
        result = utils.dataclass_from_dict(self.TestDataclass, data)

        # ASSERT
        self.assertEqual(result.name, data["name"])
        self.assertEqual(result.number, data["number"])
        self.assertEqual(result.list_of_values, data["list_of_values"])
        self.assertEqual(result.optional, data["optional"])

    def test_dataclass_from_dict_with_missing_default(self):
        """Tests dataclass_from_dict functions as expected when a value with
        a default is missing"""

        # SETUP
        data = {"name": "test", "number": 10, "list_of_values": ["value1", "value2"]}

        # CALL
        result = utils.dataclass_from_dict(self.TestDataclass, data)

        # ASSERT
        self.assertEqual(result.name, data["name"])
        self.assertEqual(result.number, data["number"])
        self.assertEqual(result.list_of_values, data["list_of_values"])
        self.assertEqual(result.optional, None)

    def test_dataclass_from_dict_raises_type_error(self):
        """Tests dataclass_from_dict raises a type error when a value is
        missing"""

        # SETUP
        data = {"number": 10}

        # CALL & ASSERT
        with self.assertRaises(TypeError):
            utils.dataclass_from_dict(self.TestDataclass, data)


@patch("dafni_cli.utils.tabulate")
class TestFormatTable(TestCase):
    """Test class to test the format_table function"""

    def test_format_table_with_no_max_widths(self, mock_tabulate):
        """Tests that tabulate is called correctly when there are no max
        column widths specified"""
        # SETUP
        headers = ["Header 1", "Header 2"]
        rows = [
            ["Row 1 Header 1", "Row 1 Header 2"],
            ["Row 2 Header 1", "Row 2 Header 2"],
        ]

        # CALL
        result = utils.format_table(headers, rows)

        # ASSERT
        mock_tabulate.assert_called_once_with(rows, headers, **TABULATE_ARGS)
        self.assertEqual(mock_tabulate.return_value, result)

    def test_format_table_with_one_max_column_width_without_wrapping(
        self, mock_tabulate
    ):
        """Tests that tabulate is called correctly when there is one column
        with a maximum width but it is not exceeded"""
        # SETUP
        headers = ["Header 1", "Header 2"]
        rows = [
            ["Row 1 Header 1", "Row 1 Header 2"],
            ["Row 2 Header 1", "Row 2 Header 2"],
        ]
        max_column_widths = [None, 40]

        # CALL
        result = utils.format_table(headers, rows, max_column_widths)

        # ASSERT
        mock_tabulate.assert_called_once_with(rows, headers, **TABULATE_ARGS)
        self.assertEqual(mock_tabulate.return_value, result)

    def test_format_table_with_one_max_column_width_with_wrapping(self, mock_tabulate):
        """Tests that tabulate is called correctly when there is one column
        with a maximum width and it is exceeded by a value"""
        # SETUP
        headers = ["Header 1", "Header 2"]
        rows = [
            ["Row 1 Header 1", "Row 1 Header 2"],
            ["Row 2 Header 1", "Row 2 Header 2"],
        ]
        max_column_widths = [None, 10]

        # CALL
        result = utils.format_table(headers, rows, max_column_widths)

        # ASSERT
        mock_tabulate.assert_called_once_with(
            [
                ["Row 1 Header 1", "Row 1\nHeader 2"],
                ["Row 2 Header 1", "Row 2\nHeader 2"],
            ],
            headers,
            **TABULATE_ARGS,
        )
        self.assertEqual(mock_tabulate.return_value, result)

    def test_format_table_with_column_width_without_wrapping(self, mock_tabulate):
        """Tests that tabulate is called correctly when all columns have
        a maximum width but it is not exceeded"""
        # SETUP
        headers = ["Header 1", "Header 2"]
        rows = [
            ["Row 1 Header 1", "Row 1 Header 2"],
            ["Row 2 Header 1", "Row 2 Header 2"],
        ]
        max_column_widths = [40, 40]

        # CALL
        result = utils.format_table(headers, rows, max_column_widths)

        # ASSERT
        mock_tabulate.assert_called_once_with(rows, headers, **TABULATE_ARGS)
        self.assertEqual(mock_tabulate.return_value, result)

    def test_format_table_with_column_width_with_wrapping(self, mock_tabulate):
        """Tests that tabulate is called correctly when all columns have
        a maximum width and it is exceeded by a value"""
        # SETUP
        headers = ["Header 1", "Header 2"]
        rows = [
            ["Row 1 Header 1", "Row 1 Header 2"],
            ["Row 2 Header 1", "Row 2 Header 2"],
        ]
        max_column_widths = [10, 10]

        # CALL
        result = utils.format_table(headers, rows, max_column_widths)

        # ASSERT
        mock_tabulate.assert_called_once_with(
            [
                ["Row 1\nHeader 1", "Row 1\nHeader 2"],
                ["Row 2\nHeader 1", "Row 2\nHeader 2"],
            ],
            headers,
            **TABULATE_ARGS,
        )
        self.assertEqual(mock_tabulate.return_value, result)


class TestFormatDatetime(TestCase):
    """Test class to test the format_datetime function"""

    def test_formats_correctly_when_include_time_false(self):
        """Tests the expected string is returned when include_time is False"""
        # SETUP
        test_value = datetime(2021, 3, 16, 9, 27, 21)

        # CALL
        result = utils.format_datetime(test_value, include_time=False)

        # ASSERT
        self.assertEqual(result, test_value.strftime(DATE_OUTPUT_FORMAT))

    def test_formats_correctly_when_include_time_true(self):
        """Tests the expected string is returned when include_time is True"""
        # SETUP
        test_value = datetime(2021, 3, 16, 9, 27, 21)

        # CALL
        result = utils.format_datetime(test_value, include_time=True)

        # ASSERT
        self.assertEqual(result, test_value.strftime(DATE_TIME_OUTPUT_FORMAT))

    def test_returns_none_when_value_none_and_include_time_false(self):
        """Tests the expected string is returned when include_time is False
        and the given datetime value is None"""
        # SETUP
        test_value = None

        # CALL
        result = utils.format_datetime(test_value, include_time=False)

        # ASSERT
        self.assertEqual(result, "N/A")

    def test_returns_none_when_value_none_and_include_time_true(self):
        """Tests the expected string is returned when include_time is True
        and the given datetime value is None"""
        # SETUP
        test_value = None

        # CALL
        result = utils.format_datetime(test_value, include_time=True)

        # ASSERT
        self.assertEqual(result, "N/A")


class TestIsValidURL(TestCase):
    """Test class to test the is_valid_url function"""

    def test_valid_url_returns_true(self):
        """Tests that a valid URL returns True"""
        self.assertTrue(utils.is_valid_url("https://www.somewebsite.com/"))

    def test_invalid_url_returns_false(self):
        """Tests that an invalid URL returns False"""
        self.assertFalse(utils.is_valid_url("some text"))
        self.assertFalse(utils.is_valid_url(""))

    @patch("dafni_cli.utils.urlparse")
    def test_valid_url_returns_false_on_value_error(self, mock_urlparse):
        """Tests that False is returned when a ValueError occurs"""
        mock_urlparse.side_effect = ValueError
        self.assertFalse(utils.is_valid_url("https://www.somewebsite.com/"))


class TestIsValidEmailAddress(TestCase):
    """Test class to test the is_valid_email_address function"""

    def test_valid_email_returns_true(self):
        """Tests that a valid email address returns True"""
        self.assertTrue(utils.is_valid_email_address("test@example.com"))

    def test_invalid_email_returns_false(self):
        """Tests that an invalid email address returns False"""
        self.assertFalse(utils.is_valid_email_address(""))
        self.assertFalse(utils.is_valid_email_address("some text"))
        self.assertFalse(utils.is_valid_email_address("test@example"))


class TestFormatDataFormat(TestCase):
    """Test class to test the format_data_format function"""

    def test_formats_correctly(self):
        """Tests that passing a valid format returns the correct value"""

        for key in DATA_FORMATS.keys():
            result = utils.format_data_format(key)
            self.assertEqual(result, DATA_FORMATS[key])

    def test_formats_invalid_values_correctly(self):
        """Tests that passing an invalid format returns the correct value"""
        self.assertEqual(
            utils.format_data_format("invalid/format"), OUTPUT_UNKNOWN_FORMAT
        )

    def test_formats_none_correctly(self):
        """Tests that passing None returns the correct value"""
        self.assertEqual(utils.format_data_format(None), OUTPUT_UNKNOWN_FORMAT)


class TestConstructValidationErrorsFromDict(TestCase):
    """Test class to test the construct_validation_errors_from_dict function"""

    def test_formats_correctly(self):
        """Tests construct_validation_errors_from_dict works correctly"""

        dictionary = {
            "metadata": {
                "description": ["This field is required"],
                "nested": {"error": "test"},
            },
            "more_errors": {"hello": "world"},
        }

        result = utils.construct_validation_errors_from_dict(dictionary)

        self.assertEqual(
            result,
            [
                "Error: ( metadata -> description ) - This field is required",
                "Error: ( metadata -> nested -> error ) - test",
                "Error: ( more_errors -> hello ) - world",
            ],
        )


@patch("dafni_cli.utils.click")
class TestOptionalEcho(TestCase):
    """Test class to test the optional_echo function"""

    def test_outputs_when_passed_false(self, mock_click):
        """Tests optional_echo calls click.echo when passed a value of False"""
        # SETUP
        message = MagicMock()

        # CALL
        utils.optional_echo(message, False)

        # ASSERT
        mock_click.echo.assert_called_once_with(message)

    def test_does_not_output_when_passed_true(self, mock_click):
        """Tests optional_echo calls click.echo when passed a value of True"""
        # SETUP
        message = MagicMock()

        # CALL
        utils.optional_echo(message, True)

        # ASSERT
        mock_click.echo.assert_not_called()


@patch("dafni_cli.utils.tqdm")
class TestCreateFileProgressBar(TestCase):
    """Test class to test the create_file_progress_bar function"""

    def test_create_file_progress_bar(self, mock_tqdm):
        """Tests create_file_progress_bar calls tqdm correctly"""

        # SETUP
        description = MagicMock()
        total = MagicMock()
        disable = MagicMock()

        # CALL
        result = utils.create_file_progress_bar(
            description=description, total=total, disable=disable
        )

        # ASSERT
        mock_tqdm.assert_called_once_with(
            desc=description,
            total=total,
            miniters=1,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            disable=disable,
        )
        self.assertEqual(result, mock_tqdm.return_value)


@patch("dafni_cli.utils.create_file_progress_bar")
class TestOverallFileProgressBar(TestCase):
    """Test class to test the OverallFileProgressBar class functions
    correctly"""

    def test_overall_file_progress_bar(self, mock_create_file_progress_bar):
        """Tests that the OverallFileProgressBar class functions correctly"""

        # SETUP
        total_files = 10
        total_size = MagicMock()
        disable = MagicMock()

        mock_progress_bar = MagicMock()
        mock_create_file_progress_bar.return_value = mock_progress_bar

        # CALL & ASSERT
        with utils.OverallFileProgressBar(
            total_files=total_files, total_size=total_size, disable=disable
        ) as overall_progress_bar:
            # Should have just created a progress bar
            mock_create_file_progress_bar.assert_called_once_with(
                description=f"Overall progress 0/{total_files}",
                total=total_size,
                disable=disable,
            )
            self.assertEqual(overall_progress_bar._progress_bar, mock_progress_bar)

            # Try updating the bar
            file_size = MagicMock()
            overall_progress_bar.update(file_size=file_size)
            mock_progress_bar.set_description.assert_called_with(
                f"Overall progress 1/{total_files}"
            )
            mock_progress_bar.update.assert_called_once()

        mock_progress_bar.close.assert_called_once()


class TestIsValidDefinitionFile(TestCase):
    def test_true_returned_if_correct_definition_file_type(self):
        valid_file_types = ("yml", "yaml", "json")
        for file_type in valid_file_types:
            # SETUP
            file_name = Path("path/to/definition." + file_type)
            # CALL
            result = utils.is_valid_definition_file(file_name)
            # ASSERT
            self.assertTrue(result)

    def test_false_returned_if_incorrect_definition_file_type(self):
        # SETUP
        file_name = Path("path/to/definition.txt")

        # CALL
        result = utils.is_valid_definition_file(file_name)

        # ASSERT
        self.assertFalse(result)

    def test_false_returned_if_no_definition_file_type_given(self):
        # SETUP
        file_name = Path("path/to/defintion")

        # CALL
        result = utils.is_valid_definition_file(file_name)

        # ASSERT
        self.assertFalse(result)


class TestIsValidImageFile(TestCase):
    """Test class to test the is_valid_image_file function"""

    def test_true_returned_if_correct_file_type_is_given(self):
        """Tests is_valid_image_file returns true when passed a correct file type"""
        # SETUP
        file_names = [Path("path/to/image.tar"), Path("path/to/image.tar.gz")]

        for file_name in file_names:
            # CALL
            result = utils.is_valid_image_file(file_name)

            # ASSERT
            self.assertTrue(result)

    def test_false_returned_if_incorrect_file_type_is_given(self):
        """Tests is_valid_image_file returns false when passed an incorrect file type"""
        # SETUP
        file_name = Path("path/to/image.txt")

        # CALL
        result = utils.is_valid_image_file(file_name)

        # ASSERT
        self.assertFalse(result)

    def test_false_returned_if_path_given_without_file_type(self):
        """Tests is_valid_image_file returns false when passed a file path without a file type"""
        # SETUP
        file_name = Path("path/to/image")

        # CALL
        result = utils.is_valid_image_file(file_name)

        # ASSERT
        self.assertFalse(result)


class TestSplitList(TestCase):
    """Test class to test the split_list function"""

    def test_no_splitting_when_shorter_than_max_size(self):
        """Tests split_list returns a generator that produces a list containing
        the unmodified list when its length is shorter than max_size"""
        # SETUP
        list_length = 20
        max_size = 100
        lst = range(list_length)

        # CALL
        result = list(utils.split_list(lst=lst, max_size=max_size))

        # ASSERT
        self.assertEqual(result, [lst])

    def test_splits_when_longer_than_max_size_when_fits_exactly(self):
        """Tests split_list returns a generator that produces a list containing
        many shorter lists not exceeding max_size when its length is longer
        than max_size and the split list elements are all the same size"""
        # SETUP
        list_length = 20
        max_size = 2
        lst = list(range(list_length))

        # CALL
        result = list(utils.split_list(lst=lst, max_size=max_size))

        # ASSERT
        self.assertEqual(
            result,
            [list(range(i, i + max_size)) for i in range(0, list_length, max_size)],
        )

    def test_splits_when_longer_than_max_size_when_does_not_fit_exactly(self):
        """Tests split_list returns a generator that produces a list containing
        many shorter lists not exceeding max_size when its length is longer
        than max_size and the array cannot be split into exact chunks"""
        # SETUP
        list_length = 20
        max_size = 15
        lst = list(range(list_length))

        # CALL
        result = list(utils.split_list(lst=lst, max_size=max_size))

        # ASSERT
        self.assertEqual(
            result,
            [list(range(0, max_size)), list(range(max_size, list_length))],
        )


@freeze_time("2000-01-10")
class TestGetCurrentMessages(TestCase):
    """Test class to test the get_current_messages function"""

    def test_returns_correct_messages_from_list(self):
        # SETUP
        mock_notifications = [
            {
                "start_date": datetime(2000, 1, 1),
                "end_date": datetime(2000, 1, 20),
                "message": "this will be returned",
            },
            {
                "start_date": datetime(2000, 1, 15),
                "end_date": datetime(2000, 1, 20),
                "message": "this will not be returned",
            },
            {
                "start_date": datetime(2000, 1, 1),
                "end_date": datetime(2000, 1, 10),
                "message": "this will not be returned",
            },
        ]
        expected_result = ["this will be returned"]

        # CALL
        result = utils.get_current_messages(mock_notifications)

        # ASSERT
        self.assertEqual(result, expected_result)
