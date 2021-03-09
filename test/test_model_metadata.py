import unittest
from dafni_cli.model_metadata import *


class TestOptionalColumn(unittest.TestCase):
    def test_if_key_exists_value_is_returned_with_correct_width(self):
        # SETUP
        key = "key"
        value = "value"
        dictionary = {key: value}
        column_width = 10

        # CALL
        entry = optional_column(dictionary, key, column_width)

        # ASSERT
        self.assertEqual(entry, "value     ")

    def test_if_key_exists_value_is_returned_with_correct_width_and_alignment(self):
        # SETUP
        key = "key"
        value = "value"
        dictionary = {key: value}
        column_width = 10
        alignment = ">"

        # CALL
        entry = optional_column(dictionary, key, column_width, alignment)

        # ASSERT
        self.assertEqual(entry, "     value")

    def test_if_key_exists_and_no_column_width_specified(self):
        # SETUP
        key = "key"
        value = "value"
        dictionary = {key: value}

        # CALL
        entry = optional_column(dictionary, key)

        # ASSERT
        self.assertEqual(entry, "value")

    def test_if_key_does_not_exist_but_column_width_specified(self):
        # SETUP
        key = "key"
        dictionary = {"other_key": "value"}
        column_width = 8

        # CALL
        entry = optional_column(dictionary, key, column_width)

        # ASSERT
        self.assertEqual(entry, " " * 8)

    def test_if_key_does_not_exist_but_column_width_not_specified(self):
        # SETUP
        key = "key"
        dictionary = {"other_key": "value"}

        # CALL
        entry = optional_column(dictionary, key)

        # ASSERT
        self.assertEqual(entry, "")

    def test_exception_raised_when_column_width_negative(self):
        # SETUP
        key = "key"
        value = "value"
        dictionary = {key: value}

        # CALL
        # ASSERT
        self.assertRaises(ValueError, optional_column, dictionary, key, -1)
