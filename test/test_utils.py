from dataclasses import dataclass
import os
import tempfile
from io import BytesIO
from typing import List, Optional
from unittest import TestCase
from unittest.mock import call, patch
from zipfile import ZipFile

from dafni_cli import utils


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


class TestOptionalColumn(TestCase):
    """Test class to test the 'optional_column' function"""

    def test_formatted_correctly_with_default_alignment(self):
        """Tests that if the given value is not None it is returned as a
        string with the correct number of spaces added"""

        # SETUP
        column_width = 10

        values_and_results = [
            ("value", "value     "),
            (1, "1         "),
            (1.0, "1.0       "),
            ({"sub_key": "value"}, "{'sub_key': 'value'}"),
            ({}, "{}        "),
            ([], "[]        "),
            ([1, 2], "[1, 2]    "),
            (True, "True      "),
        ]

        # CALL & ASSERT
        for value, result in values_and_results:
            self.assertEqual(utils.optional_column(value, column_width), result)

    def test_formatted_correctly_with_given_alignment(self):
        """Tests that if the given value is not None it is returned as a
        string with the correct number of spaces added using the given
        alignment"""

        # SETUP
        column_width = 10
        alignment = ">"

        values_and_results = [
            ("value", "     value"),
            (1, "         1"),
            (1.0, "       1.0"),
            ({"sub_key": "value"}, "{'sub_key': 'value'}"),
            ({}, "        {}"),
            ([], "        []"),
            ([1, 2], "    [1, 2]"),
            (True, "      True"),
        ]

        # CALL & ASSERT
        for value, result in values_and_results:
            self.assertEqual(
                utils.optional_column(value, column_width, alignment), result
            )

    def test_formatted_correctly_with_no_specified_column_width(self):
        """Tests that if the given value is not None it is returned as a
        string with no spaces added when the column_width isn't specified"""

        # SETUP
        values_and_results = [
            ("value", "value"),
            (1, "1"),
            (1.0, "1.0"),
            ({"sub_key": "value"}, "{'sub_key': 'value'}"),
            ({}, "{}"),
            ([], "[]"),
            ([1, 2], "[1, 2]"),
            (True, "True"),
        ]

        # CALL & ASSERT
        for value, result in values_and_results:
            self.assertEqual(utils.optional_column(value), result)

    def test_spaces_returned_when_value_is_none(self):
        """Tests that if the given value is None a string of spaces with the
        given width is returned"""

        # CALL
        result = utils.optional_column(None, 8)

        # ASSERT
        self.assertEqual(result, "        ")

    def test_spaces_returned_when_value_is_none_and_no_width_specified(self):
        """Tests that if the given value is None and the column_width isn't
        assigned then an empty string is returned"""

        # CALL
        result = utils.optional_column(None)

        # ASSERT
        self.assertEqual(result, "")

    def test_value_error_raised_when_width_negative(self):
        """Tests that if the column width is negative a ValueError is raised"""

        # CALL
        with self.assertRaises(ValueError) as err:
            utils.optional_column("", -1)

        # ASSERT
        self.assertEqual(
            str(err.exception), "Column width for optional column must be non-negative"
        )

    def test_value_error_raised_when_width_negative_and_value_none(self):
        """Tests that if the column width is negative and the value is None
        a ValueError is raised"""

        # CALL
        with self.assertRaises(ValueError) as err:
            utils.optional_column(None, -1)

        # ASSERT
        self.assertEqual(
            str(err.exception), "Column width for optional column must be non-negative"
        )


class TestProcessDateFilter(TestCase):
    """Test class to test the process_date_filter function"""

    def test_valid_date_strings_are_formatted_correctly(self):
        """Tests that valid date strings are formatted correctly"""

        # SETUP
        values_and_results = [
            ("1/2/2003", "2003-02-01T00:00:00"),
            ("10/2/2003", "2003-02-10T00:00:00"),
            ("10/12/2003", "2003-12-10T00:00:00"),
        ]

        # CALL & ASSERT
        for value, result in values_and_results:
            self.assertEqual(result, utils.process_date_filter(value))

    def test_value_error_raised_if_given_invalid_date(self):
        """Tests that invalid date strings raise ValueError's"""

        # SETUP
        values = ["1/1/21", "1/13/2021", "32/2/2021"]

        # CALL & ASSERT
        for value in values:
            with self.assertRaises(ValueError):
                utils.process_date_filter(value)


class TestOutputTableRow(TestCase):
    """Test class to test the output_table_row function"""

    def test_table_header_string_processed_correctly_with_default_alignment(self):
        """Tests that table headers are processed correctly using the default
        alignment"""

        # SETUP
        values_and_results = [
            (["Column_1"], [10], "Column_1  \n-----------\n"),
            (
                ["Column_1", "Column_2", "Column_3"],
                [10, 11, 12],
                "Column_1   Column_2    Column_3    \n------------------------------------\n",
            ),
        ]

        # CALL & ASSERT
        for columns, widths, result in values_and_results:
            self.assertEqual(
                utils.output_table_row(columns, widths, header=True), result
            )

    def test_table_header_string_processed_correctly_with_alignment_given_for_multiple_columns(
        self,
    ):
        """Tests that table headers are processed correctly when an alignment
        is given for multiple columns"""

        # SETUP
        columns = ["Column_1", "Column_2", "Column_3"]
        widths = [10, 11, 12]
        values_and_results = [
            (
                "<",
                "Column_1   Column_2    Column_3    \n------------------------------------\n",
            ),
            (
                "^",
                " Column_1   Column_2     Column_3  \n------------------------------------\n",
            ),
            (
                ">",
                "  Column_1    Column_2     Column_3\n------------------------------------\n",
            ),
        ]

        # CALL & ASSERT
        for alignment, result in values_and_results:
            self.assertEqual(
                utils.output_table_row(
                    columns, widths, alignment=alignment, header=True
                ),
                result,
            )

    def test_table_header_string_processed_correctly_with_alignment_given_for_single_column(
        self,
    ):
        """Tests that table headers are processed correctly when an alignment
        is given for a single column"""

        # SETUP
        columns = ["Column_1"]
        widths = [10]
        values_and_results = [
            (
                "<",
                "Column_1  \n-----------\n",
            ),
            (
                "^",
                " Column_1 \n-----------\n",
            ),
            (
                ">",
                "  Column_1\n-----------\n",
            ),
        ]

        # CALL & ASSERT
        for alignment, result in values_and_results:
            self.assertEqual(
                utils.output_table_row(
                    columns, widths, alignment=alignment, header=True
                ),
                result,
            )

    def test_table_row_string_processed_correctly_with_default_alignment(self):
        """Tests that a table row is processed correctly using the default
        alignment"""

        # SETUP
        values_and_results = [
            (["Value_1"], [10], "Value_1   \n"),
            (
                ["Value_1", "Value_2", "Value_3"],
                [10, 11, 12],
                "Value_1    Value_2     Value_3     \n",
            ),
        ]

        # CALL & ASSERT
        for entries, widths, result in values_and_results:
            self.assertEqual(utils.output_table_row(entries, widths), result)

    def test_table_row_string_processed_correctly_with_alignment_given_for_multiple_entries(
        self,
    ):
        """Tests that a table row is processed correctly when an alignment
        is given for multiple entries"""

        # SETUP
        entries = ["Value_1", "Value_2", "Value_3"]
        widths = [10, 11, 12]
        values_and_results = [
            (
                "<",
                "Value_1    Value_2     Value_3     \n",
            ),
            (
                "^",
                " Value_1     Value_2     Value_3   \n",
            ),
            (
                ">",
                "   Value_1     Value_2      Value_3\n",
            ),
        ]

        # CALL & ASSERT
        for alignment, result in values_and_results:
            self.assertEqual(
                utils.output_table_row(entries, widths, alignment=alignment), result
            )

    def test_table_row_string_processed_correctly_with_alignment_given_for_single_entry(
        self,
    ):
        """Tests that a table row is processed correctly when an alignment
        is given for a single entries"""

        # SETUP
        entries = ["Value_1"]
        widths = [10]
        values_and_results = [
            (
                "<",
                "Value_1   \n",
            ),
            (
                "^",
                " Value_1  \n",
            ),
            (
                ">",
                "   Value_1\n",
            ),
        ]

        # CALL & ASSERT
        for alignment, result in values_and_results:
            self.assertEqual(
                utils.output_table_row(entries, widths, alignment=alignment), result
            )


@patch("dafni_cli.utils.output_table_row")
class TestOutputTable(TestCase):
    """Test class to test the output_table function"""

    def test_correct_table_str_returned_for_single_column_table_with_default_alignment(
        self, mock_output
    ):
        """Tests that the correct string is returned for a single column table
        with the default alignment"""

        # SETUP
        columns = ["Column_1"]
        rows = [["Value_1"]]
        widths = [10]
        # Setup output_table_row to return the first column/value passed in
        mock_output.side_effect = "Column_1  \n----------\n", "Value_1   \n"

        # CALL
        result = utils.output_table(columns, widths, rows)

        # ASSERT
        self.assertEqual(result, "Column_1  \n----------\nValue_1   \n")
        mock_output.assert_has_calls(
            [
                call(columns, widths, "<", header=True),
                call(rows[0], widths, "<"),
            ]
        )

    def test_correct_table_str_returned_for_multiple_column_and_row_table_with_default_alignment(
        self, mock_output
    ):
        """Tests that the correct string is returned for a table with multiple
        columns and the default alignment"""
        # SETUP
        columns = ["Column_1", "Column_2"]
        rows = [["Value_1", "Value_2"], ["Value_3", "Value_4"]]
        widths = [10]
        # setup output_table_row to return the firs column/value passed in
        mock_output.side_effect = (
            "Column_1  Column_2   \n----------\n",
            "Value_1   Value_2    \n",
            "Value_3   Value_4    \n",
        )

        # CALL
        result = utils.output_table(columns, widths, rows)

        # ASSERT
        self.assertEqual(
            result,
            "Column_1  Column_2   \n----------\nValue_1   Value_2    \nValue_3   Value_4    \n",
        )
        mock_output.assert_has_calls(
            [
                call(columns, widths, "<", header=True),
                call(rows[0], widths, "<"),
                call(rows[1], widths, "<"),
            ]
        )


class TestProcessFileSize(TestCase):
    """Test class to test the process_file_size functionality"""

    def test_empty_string_returned_if_non_integer_or_float_value_given(self):
        """Tests that an empty string is returned if the given file size is
        an invalid type"""

        # SETUP
        values = [[12], (12, 13)]

        # CALL & ASSERT
        for file_size in values:
            self.assertEqual(utils.process_file_size(file_size), "")

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
            self.assertEqual(utils.process_file_size(file_size), result)


@patch("dafni_cli.utils.click")
class TestArgumentConfirmation(TestCase):
    """Test class to test the argument_confirmation function"""

    def test_arguments_are_printed_correctly_without_additional_messages(
        self, mock_click
    ):
        """Tests that the arguments are printed correctly and the right calls
        are made to click"""
        # SETUP
        argument_names = ["arg 1", "arg 2", "arg 3"]
        arguments = ["string option", "12", "{'key': 'value'}"]
        confirmation_message = "confirmation message"

        # CALL
        utils.argument_confirmation(argument_names, arguments, confirmation_message)

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
        argument_names = ["arg 1", "arg 2", "arg 3"]
        arguments = ["string option", "12", "{'key': 'value'}"]
        confirmation_message = "confirmation message"
        additional_messages = ["additional message 1", "additional message 2"]

        # CALL
        utils.argument_confirmation(
            argument_names, arguments, confirmation_message, additional_messages
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


class TestWriteFilesToZip(TestCase):
    """Test class to test the write_files_to_zip function"""

    def test_given_files_written_as_zip_file_to_given_location_with_correct_contents(
        self,
    ):
        """Tests write_files_to_zip writes files as a zip to the specified location
        with the correct contents"""
        # SETUP
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "test.zip")

            file_names = ["file_1.txt", "file_2.txt"]
            file_contents = [BytesIO(b"Test text 1"), BytesIO(b"Test text 2")]

            # CALL
            utils.write_files_to_zip(zip_path, file_names, file_contents)

            # ASSERT
            self.assertTrue(os.path.exists(zip_path))
            with ZipFile(zip_path, "r") as zipObj:
                self.assertEqual(zipObj.namelist(), file_names)

                for idx, name in enumerate(file_names):
                    with zipObj.open(name, "r") as zip_file:
                        self.assertEqual(zip_file.read(), file_contents[idx].getvalue())


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
