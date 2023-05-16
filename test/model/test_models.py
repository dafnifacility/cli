from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.model.inputs import ModelInputs
from dafni_cli.model.model import Model, ModelSpec, parse_model, parse_models

from test.fixtures.models import (
    TEST_MODEL,
    TEST_MODEL_DATA_MODELS_ENDPOINT,
    TEST_MODEL_METADATA,
    TEST_MODEL_SPEC,
    TEST_MODEL_SPEC_DEFAULT,
    TEST_MODELS,
)


class TestModelSpec(TestCase):
    """Tests the ModelSpec dataclass"""

    def test_parse(self):
        """Tests parsing of ModelSpec"""
        model_spec: ModelSpec = ParserBaseObject.parse_from_dict(
            ModelSpec, TEST_MODEL_SPEC
        )

        self.assertEqual(model_spec.image_url, TEST_MODEL_SPEC["image"])

        # ModelInputs (contents tested in TestModelInputs)
        self.assertEqual(type(model_spec.inputs), ModelInputs)

        # ModelOutputs (contents tested in TestModelOutputs)
        self.assertEqual(type(model_spec.inputs), ModelInputs)

    def test_parse_default(self):
        """Tests parsing of ModelSpec when all optional values are excluded"""
        model_spec: ModelSpec = ParserBaseObject.parse_from_dict(
            ModelSpec, TEST_MODEL_SPEC_DEFAULT
        )

        self.assertEqual(model_spec.image_url, TEST_MODEL_SPEC["image"])

        self.assertEqual(model_spec.inputs, None)
        self.assertEqual(model_spec.outputs, None)


class TestModel(TestCase):
    """Tests the Model dataclass"""

    def test_parse_models(self):
        """Tests parsing of models using test data for the /models endpoint"""
        models = parse_models(TEST_MODELS)

        self.assertEqual(len(models), 1)

        model1 = models[0]
        model1_dict = TEST_MODELS[0]
        self.assertEqual(model1.model_id, model1_dict["id"])
        self.assertEqual(model1.kind, model1_dict["kind"])
        self.assertEqual(model1.owner_id, model1_dict["owner"])
        self.assertEqual(model1.parent_id, model1_dict["parent"])
        self.assertEqual(
            model1.creation_date,
            datetime(2019, 7, 17, 13, 33, 13, 751682, tzinfo=tzutc()),
        )
        self.assertEqual(
            model1.publication_date,
            datetime(2020, 4, 2, 9, 12, 25, 989915, tzinfo=tzutc()),
        )
        self.assertEqual(model1.version_message, model1_dict["version_message"])
        self.assertEqual(model1.version_tags, model1_dict["version_tags"])

        # VersionHistory
        self.assertEqual(len(model1.version_history), 1)
        self.assertEqual(
            model1.version_history[0].version_id,
            model1_dict["version_history"][0]["id"],
        )
        self.assertEqual(
            model1.version_history[0].version_message,
            model1_dict["version_history"][0]["version_message"],
        )
        self.assertEqual(
            model1.version_history[0].version_tags,
            model1_dict["version_history"][0]["version_tags"],
        )
        self.assertEqual(
            model1.version_history[0].publication_date,
            datetime(2020, 4, 2, 9, 12, 25, 989915, tzinfo=tzutc()),
        )

        # Auth tested in test_auth anyway
        self.assertEqual(type(model1.auth), Auth)
        self.assertEqual(
            model1.ingest_completed_date,
            None,
        )

        self.assertEqual(model1.api_version, None)
        self.assertEqual(model1.container, None)
        self.assertEqual(model1.container_version, None)
        self.assertEqual(model1.type, model1_dict["type"])
        self.assertEqual(model1.spec, None)

        # Ensure the metadata is correct
        self.assertEqual(
            model1.metadata.display_name,
            TEST_MODEL_DATA_MODELS_ENDPOINT["display_name"],
        )
        self.assertEqual(model1.metadata.name, TEST_MODEL_DATA_MODELS_ENDPOINT["name"])
        self.assertEqual(
            model1.metadata.summary, TEST_MODEL_DATA_MODELS_ENDPOINT["summary"]
        )
        self.assertEqual(
            model1.metadata.status, TEST_MODEL_DATA_MODELS_ENDPOINT["status"]
        )
        self.assertEqual(model1.metadata.description, None)
        self.assertEqual(model1.metadata.publisher, None)
        self.assertEqual(model1.metadata.source_code, None)

    def test_parse_model(self):
        """Tests parsing of a model using test data for the /model/<version_id>
        endpoint"""
        model = parse_model(TEST_MODEL)

        self.assertEqual(model.model_id, TEST_MODEL["id"])
        self.assertEqual(model.kind, TEST_MODEL["kind"])
        self.assertEqual(model.owner_id, TEST_MODEL["owner"])
        self.assertEqual(model.parent_id, TEST_MODEL["parent"])
        self.assertEqual(
            model.creation_date,
            datetime(2019, 7, 17, 13, 33, 13, 751682, tzinfo=tzutc()),
        )
        self.assertEqual(
            model.publication_date,
            datetime(2020, 4, 2, 9, 12, 25, 989915, tzinfo=tzutc()),
        )
        self.assertEqual(model.version_message, TEST_MODEL["version_message"])
        self.assertEqual(model.version_tags, TEST_MODEL["version_tags"])

        # VersionHistory
        self.assertEqual(len(model.version_history), 1)
        self.assertEqual(
            model.version_history[0].version_id,
            TEST_MODEL["version_history"][0]["id"],
        )
        self.assertEqual(
            model.version_history[0].version_message,
            TEST_MODEL["version_history"][0]["version_message"],
        )
        self.assertEqual(
            model.version_history[0].version_tags,
            TEST_MODEL["version_history"][0]["version_tags"],
        )
        self.assertEqual(
            model.version_history[0].publication_date,
            datetime(2020, 4, 2, 9, 12, 25, 989915, tzinfo=tzutc()),
        )

        # Auth tested in test_auth anyway
        self.assertEqual(type(model.auth), Auth)
        self.assertEqual(
            model.ingest_completed_date,
            None,
        )

        self.assertEqual(model.api_version, TEST_MODEL["api_version"])
        self.assertEqual(model.container, TEST_MODEL["container"])
        self.assertEqual(model.container_version, TEST_MODEL["container_version"])
        self.assertEqual(model.type, TEST_MODEL["type"])

        # Model spec (contents tested in TestModelSpec)
        self.assertEqual(type(model.spec), ModelSpec)

        # Ensure the metadata is correct
        self.assertEqual(
            model.metadata.display_name, TEST_MODEL_METADATA["display_name"]
        )
        self.assertEqual(model.metadata.name, TEST_MODEL_METADATA["name"])
        self.assertEqual(model.metadata.summary, TEST_MODEL_METADATA["summary"])
        self.assertEqual(model.metadata.status, TEST_MODEL_METADATA["status"])
        self.assertEqual(model.metadata.description, TEST_MODEL_METADATA["description"])
        self.assertEqual(model.metadata.publisher, TEST_MODEL_METADATA["publisher"])
        self.assertEqual(model.metadata.source_code, TEST_MODEL_METADATA["source_code"])

    def _test_filter_by_date(
        self, model: Model, key: str, date_str: str, expected_output: bool
    ):
        """Utility function to check a particular set of parameters to
        filter_by_date does what is expected"""
        self.assertEqual(model.filter_by_date(key, date_str), expected_output)

    def test_filter_by_date(self):
        """Tests filter_by_date works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # Creation date and publication date's are:
        # 2019-07-17 13:33:13.751682+00:00
        # 2020-04-02 09:12:25.989915+00:00

        # CALL

        # Before
        self._test_filter_by_date(model, "creation", "16/05/2018", True)
        self._test_filter_by_date(model, "publication", "16/05/2018", True)
        # Equal
        self._test_filter_by_date(model, "creation", "17/07/2019", True)
        self._test_filter_by_date(model, "publication", "02/04/2020", True)
        # After
        self._test_filter_by_date(model, "creation", "11/08/2019", False)
        self._test_filter_by_date(model, "publication", "16/05/2022", False)

    def test_filter_by_date_error(self):
        """Tests filter_by_date raises an error if the key is wrong"""
        # SETUP
        model = parse_model(TEST_MODEL)

        with self.assertRaises(KeyError):
            model.filter_by_date("key", "11/12/2020")

    @patch("dafni_cli.model.model.click")
    def test_output_details(self, mock_click):
        """Tests output_details works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # CALL
        model.output_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    "Name: Some display name"
                    + TAB_SPACE
                    + "ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a"
                    + TAB_SPACE
                    + "Date: July 17 2019"
                ),
                call("Summary: For testing"),
                call(""),
            ]
        )

    @patch("dafni_cli.model.model.prose_print")
    @patch("dafni_cli.model.model.click")
    def test_output_details_with_long(self, mock_click, mock_prose_print):
        """Tests output_details works correctly when 'long' is set to True"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # CALL
        model.output_details(long=True)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    "Name: Some display name"
                    + TAB_SPACE
                    + "ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a"
                    + TAB_SPACE
                    + "Date: July 17 2019"
                ),
                call("Summary: For testing"),
                call("Description: "),
                call(""),
            ]
        )
        mock_prose_print.called_once_with("description", CONSOLE_WIDTH)

    @patch("dafni_cli.model.model.prose_print")
    @patch("dafni_cli.model.model.click")
    def test_output_info(self, mock_click, mock_prose_print):
        """Tests output_info works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        model.output_info()

        mock_click.echo.assert_has_calls(
            [
                call("Name: Some display name"),
                call("Date: July 17 2019"),
                call("Summary: "),
                call("For testing"),
                call("Description: "),
                call(""),
                call("Input Parameters: "),
                call(
                    "Title       Type      Min       Max       Default  Description\n-----------------------------------------------------------------------\nYear input  integer   2016      2025      2018     Year input description\n"
                ),
                call("Input Data Slots: "),
                call(
                    "Name: Inputs\nPath in container: inputs/\nRequired: True\nDefault Datasets: \nID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000f    \n"
                ),
                call("Outputs: "),
                call(
                    "Name                 Format    Summary\n---------------------------------------------------\nexample_dataset.csv  CSV       \n"
                ),
            ]
        )
        mock_prose_print.assert_called_once_with("Test description", CONSOLE_WIDTH)

    @patch("dafni_cli.model.model.prose_print")
    @patch("dafni_cli.model.model.click")
    def test_output_info_correct_when_inputs_present_but_not_outputs(
        self, mock_click, mock_prose_print
    ):
        """Tests output_info works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)
        model.spec.outputs = None

        model.output_info()

        mock_click.echo.assert_has_calls(
            [
                call("Name: Some display name"),
                call("Date: July 17 2019"),
                call("Summary: "),
                call("For testing"),
                call("Description: "),
                call(""),
                call("Input Parameters: "),
                call(
                    "Title       Type      Min       Max       Default  Description\n-----------------------------------------------------------------------\nYear input  integer   2016      2025      2018     Year input description\n"
                ),
                call("Input Data Slots: "),
                call(
                    "Name: Inputs\nPath in container: inputs/\nRequired: True\nDefault Datasets: \nID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000f    \n"
                ),
            ]
        )
        mock_prose_print.assert_called_once_with("Test description", CONSOLE_WIDTH)

    @patch("dafni_cli.model.model.prose_print")
    @patch("dafni_cli.model.model.click")
    def test_output_info_correct_when_outputs_present_but_not_inputs(
        self, mock_click, mock_prose_print
    ):
        """Tests output_info works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)
        model.spec.inputs = None

        model.output_info()

        mock_click.echo.assert_has_calls(
            [
                call("Name: Some display name"),
                call("Date: July 17 2019"),
                call("Summary: "),
                call("For testing"),
                call("Description: "),
                call(""),
                call("Outputs: "),
                call(
                    "Name                 Format    Summary\n---------------------------------------------------\nexample_dataset.csv  CSV       \n"
                ),
            ]
        )
        mock_prose_print.assert_called_once_with("Test description", CONSOLE_WIDTH)

    @patch("dafni_cli.model.model.prose_print")
    @patch("dafni_cli.model.model.click")
    def test_output_info_correct_when_neither_inputs_nor_outputs_are_present(
        self, mock_click, mock_prose_print
    ):
        """Tests output_info works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)
        model.spec.inputs = None
        model.spec.outputs = None

        model.output_info()

        mock_click.echo.assert_has_calls(
            [
                call("Name: Some display name"),
                call("Date: July 17 2019"),
                call("Summary: "),
                call("For testing"),
                call("Description: "),
                call(""),
            ]
        )
        mock_prose_print.assert_called_once_with("Test description", CONSOLE_WIDTH)

    def test_get_version_details(self):
        """Tests get_version_details works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # CALL
        result = model.get_version_details()

        # ASSERT
        self.assertEqual(
            result,
            "ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a"
            + TAB_SPACE
            + "Name: Some display name"
            + TAB_SPACE
            + "Publication date: April 02 2020"
            + TAB_SPACE
            + "Version message: ",
        )

    @patch("dafni_cli.model.model.click")
    def test_output_version_history(self, mock_click):
        """Tests output_version_history works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # CALL
        model.output_version_history()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    "Name: Some display name"
                    + TAB_SPACE
                    + "ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000d"
                    + TAB_SPACE
                    + "Date: April 02 2020"
                ),
                call("Version message: First version"),
                call("Version tags: latest"),
                call(""),
            ]
        )