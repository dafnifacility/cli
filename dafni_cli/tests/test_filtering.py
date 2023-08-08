from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock

from dateutil.tz import tzutc

from dafni_cli import filtering


@dataclass
class TestWorkflowMetadata:
    """Dataclass storing only the metadata needed for testing workflow
    filtering"""

    display_name: str
    summary: str


@dataclass
class TestDataclass:
    """Simple dataclass for representing some test instances to pass
    to the function"""

    name: str
    description: str
    creation_date: datetime
    publication_date: datetime
    metadata: TestWorkflowMetadata
    submission_time: datetime
    finished_time: Optional[datetime]
    overall_status: str


class TestFiltering(TestCase):
    """Tests that the functions within filtering.py work correctly"""

    # Some test data
    TEST_INSTANCES = [
        TestDataclass(
            "Value1",
            "Description of object 1",
            datetime(2022, 1, 12, tzinfo=tzutc()),
            datetime(2022, 2, 12, tzinfo=tzutc()),
            TestWorkflowMetadata("Display name 1", "Simple summary 1"),
            datetime(2022, 1, 12, tzinfo=tzutc()),
            datetime(2022, 2, 12, tzinfo=tzutc()),
            "Failed",
        ),
        TestDataclass(
            "Value2",
            "Something completely different",
            datetime(2022, 8, 1, tzinfo=tzutc()),
            datetime(2022, 9, 1, tzinfo=tzutc()),
            TestWorkflowMetadata("Display name 2 test", "Simple summary 2"),
            datetime(2022, 8, 1, tzinfo=tzutc()),
            datetime(2022, 9, 1, tzinfo=tzutc()),
            "Succeeded",
        ),
        TestDataclass(
            "Value3",
            "Description of object 3",
            datetime(2023, 6, 21, tzinfo=tzutc()),
            datetime(2023, 7, 21, tzinfo=tzutc()),
            TestWorkflowMetadata("Display name 3", "Simple summary 3 test"),
            datetime(2023, 6, 21, tzinfo=tzutc()),
            None,
            "",
        ),
    ]

    TEST_DICTIONARIES = [MagicMock(), MagicMock(), MagicMock()]

    def test_filter_multiple_with_no_filters(self):
        """Tests filter_multiple does nothing when not given any filters"""
        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [], self.TEST_INSTANCES, self.TEST_DICTIONARIES
        )

        # ASSERT
        self.assertEqual(filtered_instances, self.TEST_INSTANCES)
        self.assertEqual(filtered_dictionaries, self.TEST_DICTIONARIES)

    def test_filter_multiple_with_single_filter(self):
        """Tests filter_multiple works correctly when given a single filter"""

        # SETUP
        # Simple filter to select only the second value
        def simple_filter(instance: TestDataclass):
            return instance.name == "Value2"

        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [simple_filter], self.TEST_INSTANCES, self.TEST_DICTIONARIES
        )

        # ASSERT
        self.assertEqual(filtered_instances, [self.TEST_INSTANCES[1]])
        self.assertEqual(filtered_dictionaries, [self.TEST_DICTIONARIES[1]])

    def test_with_filter_multiple_with_multiple_filters(self):
        """Tests filter_multiple works correctly when given multiple filters"""

        # SETUP
        def filter1(instance: TestDataclass):
            return "Description" in instance.description

        def filter2(instance: TestDataclass):
            return "object" in instance.description

        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filter1, filter2], self.TEST_INSTANCES, self.TEST_DICTIONARIES
        )

        # ASSERT
        self.assertEqual(
            filtered_instances, [self.TEST_INSTANCES[0], self.TEST_INSTANCES[2]]
        )
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[0], self.TEST_DICTIONARIES[2]],
        )

    def test_creation_date_filter(self):
        """Tests creation_date_filter works correctly"""
        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.creation_date_filter(datetime(2022, 8, 1))],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT
        self.assertEqual(
            filtered_instances, [self.TEST_INSTANCES[1], self.TEST_INSTANCES[2]]
        )
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[1], self.TEST_DICTIONARIES[2]],
        )

    def test_publication_date_filter(self):
        """Tests publication_date_filter works correctly"""
        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.publication_date_filter(datetime(2022, 9, 1))],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT
        self.assertEqual(
            filtered_instances, [self.TEST_INSTANCES[1], self.TEST_INSTANCES[2]]
        )
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[1], self.TEST_DICTIONARIES[2]],
        )

    def test_text_filter(self):
        """Tests text_filter works correctly"""

        # First a really broad filter

        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.text_filter("Display")],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT
        self.assertEqual(filtered_instances, self.TEST_INSTANCES)
        self.assertEqual(
            filtered_dictionaries,
            self.TEST_DICTIONARIES,
        )

        # Now for a specific one (also checking case insensitive)

        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.text_filter("suMmARy 2")],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT
        self.assertEqual(filtered_instances, [self.TEST_INSTANCES[1]])
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[1]],
        )

        # Now ensure both the display name and summary are filtered at the
        # same time

        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.text_filter("test")],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT
        self.assertEqual(
            filtered_instances, [self.TEST_INSTANCES[1], self.TEST_INSTANCES[2]]
        )
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[1], self.TEST_DICTIONARIES[2]],
        )

    def test_start_filter(self):
        """Tests start_filter works correctly"""
        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.start_filter(datetime(2022, 8, 1))],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT
        self.assertEqual(
            filtered_instances, [self.TEST_INSTANCES[1], self.TEST_INSTANCES[2]]
        )
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[1], self.TEST_DICTIONARIES[2]],
        )

    def test_end_filter(self):
        """Tests start_filter works correctly"""
        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.end_filter(datetime(2022, 9, 1))],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT

        # Here the 2nd instance has a finished_time of None, although should
        # otherwise pass
        self.assertEqual(filtered_instances, [self.TEST_INSTANCES[1]])
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[1]],
        )

    def test_status_filter(self):
        """Tests status_filter works correctly"""
        # CALL
        filtered_instances, filtered_dictionaries = filtering.filter_multiple(
            [filtering.status_filter("Succeeded")],
            self.TEST_INSTANCES,
            self.TEST_DICTIONARIES,
        )

        # ASSERT

        # Only the second status has a status of Succeeded
        self.assertEqual(filtered_instances, [self.TEST_INSTANCES[1]])
        self.assertEqual(
            filtered_dictionaries,
            [self.TEST_DICTIONARIES[1]],
        )
