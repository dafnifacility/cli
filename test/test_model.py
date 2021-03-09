import unittest
from dafni_cli.model import *
from datetime import datetime


class TestOptionalColumn(unittest.TestCase):

    def test_if_key_exists_value_is_returned_with_correct_width(self):
        # SETUP
        key = 'key'
        value = 'value'
        dictionary = {key: value}
        column_width = 10

        # CALL
        entry = optional_column(dictionary, key, column_width)

        # ASSERT
        self.assertEqual(entry, 'value     ')

    def test_if_key_exists_value_is_returned_with_correct_width_and_alignment(self):
        # SETUP
        key = 'key'
        value = 'value'
        dictionary = {key: value}
        column_width = 10
        alignment = ">"

        # CALL
        entry = optional_column(dictionary, key, column_width, alignment)

        # ASSERT
        self.assertEqual(entry, '     value')

    def test_if_key_exists_and_no_column_width_specified(self):
        # SETUP
        key = 'key'
        value = 'value'
        dictionary = {key: value}

        # CALL
        entry = optional_column(dictionary, key)

        # ASSERT
        self.assertEqual(entry, 'value')

    def test_if_key_does_not_exist_but_column_width_specified(self):
        # SETUP
        key = 'key'
        dictionary = {'other_key': 'value'}
        column_width = 8

        # CALL
        entry = optional_column(dictionary, key, column_width)

        # ASSERT
        self.assertEqual(entry, ' ' * 8)

    def test_if_key_does_not_exist_but_column_width_not_specified(self):
        # SETUP
        key = 'key'
        dictionary = {'other_key': 'value'}

        # CALL
        entry = optional_column(dictionary, key)

        # ASSERT
        self.assertEqual(entry, '')

    def test_exception_raised_when_column_width_negative(self):
        # SETUP
        key = 'key'
        value = 'value'
        dictionary = {key: value}

        # CALL
        # ASSERT
        self.assertRaises(ValueError, optional_column, dictionary, key, -1)


class TestFromDict(unittest.TestCase):
    test_dictionary = {"name": "test model name",
                       "summary": "this model is for use in tests for the Model class",
                       "description": "This is a terribly long description of the test dictionary",
                       "creation_date": "2021-01-01T00:00:00.000000Z",
                       "publication_date": "2021-01-02T00:00:00.000000Z",
                       "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                       "version_tags": ["latest"],
                       "container": "reg.dafni.rl.ac.uk/pilots/models/mobile-model/nims"}

    def test_ISO_dates_are_converted_to_datetime(self):
        # SETUP
        test_model = Model()

        # CALL
        test_model.get_details_from_dict(self.test_dictionary)

        # ASSERT
        self.assertIsNotNone(test_model.creation_time)
        self.assertIsNotNone(test_model.publication_time)
        self.assertIsInstance(test_model.creation_time, datetime)
        self.assertIsInstance(test_model.publication_time, datetime)


class TestFilterByDate(unittest.TestCase):
    # SETUP
    test_dictionary = {"name": "test model name",
                       "summary": "this model is for use in tests for the Model class",
                       "description": "This is a terribly long description of the test dictionary",
                       "creation_date": "2021-01-01T00:00:00.000000Z",
                       "publication_date": "2021-01-02T00:00:00.000000Z",
                       "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                       "version_tags": ["latest"],
                       "container": "reg.dafni.rl.ac.uk/pilots/models/mobile-model/nims"}
    test_model = Model()
    test_model.get_details_from_dict(test_dictionary)

    def test_gives_false_when_creation_date_after_given_date(self):
        # CALL
        creation_date_filter = self.test_model.filter_by_date("creation", "01/03/2021")

        # ASSERT
        self.assertFalse(creation_date_filter)

    def test_gives_false_when_publication_date_after_given_date(self):
        # CALL
        publication_date_filter = self.test_model.filter_by_date("publication", "01/03/2021")

        # ASSERT
        self.assertFalse(publication_date_filter)

    def test_gives_true_when_creation_date_before_given_date(self):
        # CALL
        creation_date_filter = self.test_model.filter_by_date("creation", "01/03/2020")

        # ASSERT
        self.assertTrue(creation_date_filter)

    def test_gives_true_when_publication_date_before_given_date(self):
        # CALL
        publication_date_filter = self.test_model.filter_by_date("publication", "01/03/2020")

        # ASSERT
        self.assertTrue(publication_date_filter)

    def test_raises_exception_when_key_is_not_creation_or_publication(self):
        # CALL
        # ASSERT
        self.assertRaises(Exception, self.test_model.filter_by_date, "not_a_key", "01/03/2020")

    def test_raises_exception_when_date_string_in_wrong_format(self):
        # CALL
        # ASSERT
        self.assertRaises(ValueError, self.test_model.filter_by_date, "creation", "2020/03/20")
