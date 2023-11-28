from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TABLE_PUBLICATION_DATE_HEADER,
    TABLE_VERSION_ID_HEADER,
    TABLE_VERSION_MESSAGE_HEADER,
    TABLE_VERSION_TAGS_HEADER,
)
from dafni_cli.models.inputs import ModelInputs
from dafni_cli.models.model import ModelMetadata, ModelSpec, parse_model, parse_models
from dafni_cli.models.outputs import ModelOutputs
from dafni_cli.tests.fixtures.models import (
    TEST_MODEL,
    TEST_MODEL_DATA_MODELS_ENDPOINT,
    TEST_MODEL_METADATA,
    TEST_MODEL_SPEC,
    TEST_MODEL_SPEC_DEFAULT,
    TEST_MODELS,
)
from dafni_cli.utils import format_datetime


class TestModelMetadata(TestCase):
    """Tests the ModelMetadata dataclass"""

    def test_parse(self):
        """Tests get_status_string"""
        model_metadata: ModelMetadata = ParserBaseObject.parse_from_dict(
            ModelMetadata, TEST_MODEL_METADATA
        )

        self.assertEqual(
            model_metadata.display_name,
            TEST_MODEL_METADATA["display_name"],
        )
        self.assertEqual(model_metadata.name, TEST_MODEL_METADATA["name"])
        self.assertEqual(model_metadata.summary, TEST_MODEL_METADATA["summary"])
        self.assertEqual(model_metadata.status, TEST_MODEL_METADATA["status"])
        self.assertEqual(model_metadata.description, TEST_MODEL_METADATA["description"])
        self.assertEqual(model_metadata.publisher, TEST_MODEL_METADATA["publisher"])
        self.assertEqual(model_metadata.source_code, TEST_MODEL_METADATA["source_code"])

    def test_get_status_string(self):
        """Tests get_status_string"""
        model_metadata: ModelMetadata = ParserBaseObject.parse_from_dict(
            ModelMetadata, TEST_MODEL_METADATA
        )

        # Check each status
        for key, value in ModelMetadata.STATUS_STRINGS.items():
            model_metadata.status = key
            self.assertEqual(model_metadata.get_status_string(), value)

        # Check an invalid status
        model_metadata.status = "InvalidKey"
        self.assertEqual(model_metadata.get_status_string(), "Unknown")


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

        self.assertEqual(model_spec.image_url, None)
        self.assertEqual(model_spec.inputs, None)
        self.assertEqual(model_spec.outputs, None)


class TestModel(TestCase):
    """Tests the Model dataclass"""

    def setUp(
        self,
    ) -> None:
        super().setUp()

        # These are used for test_output_details_*
        self.mock_inputs_format_parameters = patch.object(
            ModelInputs, "format_parameters"
        ).start()
        self.mock_inputs_format_dataslots = patch.object(
            ModelInputs, "format_dataslots"
        ).start()
        self.mock_outputs_format_outputs = patch.object(
            ModelOutputs, "format_outputs"
        ).start()

        self.addCleanup(patch.stopall)

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
        self.assertEqual(
            model.metadata.contact_point_name, TEST_MODEL_METADATA["contact_point_name"]
        )
        self.assertEqual(
            model.metadata.contact_point_email,
            TEST_MODEL_METADATA["contact_point_email"],
        )
        self.assertEqual(model.metadata.licence, TEST_MODEL_METADATA["licence"])
        self.assertEqual(model.metadata.rights, TEST_MODEL_METADATA["rights"])

    def test_get_brief_details(self):
        """Tests get_brief_details works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # CALL
        result = model.get_brief_details()

        # ASSERT
        self.assertEqual(
            result,
            [
                model.metadata.display_name,
                model.model_id,
                model.metadata.get_status_string(),
                model.auth.get_permission_string(),
                format_datetime(model.publication_date, include_time=False),
                model.metadata.summary,
            ],
        )

    @patch("dafni_cli.models.model.tabulate")
    @patch("dafni_cli.models.model.prose_print")
    @patch("dafni_cli.models.model.click")
    def test_output_details(
        self,
        mock_click,
        mock_prose_print,
        mock_tabulate,
    ):
        """Tests output_details works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # CALL
        model.output_details()

        # ASSERT
        self.mock_inputs_format_parameters.assert_called_once()
        self.mock_inputs_format_dataslots.assert_called_once()
        self.mock_outputs_format_outputs.assert_called_once()
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(
                    f"{model.metadata.display_name}  |  Status: {model.metadata.get_status_string()}  |  Tags: {', '.join(model.version_tags)}"
                ),
                call(""),
                call(f"Published by: {str(model.metadata.publisher)}"),
                call(
                    f"Contact Point: {model.metadata.contact_point_name} ({model.metadata.contact_point_email})"
                ),
                call(""),
                call(mock_tabulate.return_value),
                call(""),
                call("Version message:"),
                call(model.version_message),
                call(""),
                call("Summary:"),
                call(model.metadata.summary),
                call(""),
                call("Description:"),
                call(""),
                call("Source code:"),
                call(model.metadata.source_code),
                call(f"Licence: {model.metadata.licence}"),
                call(f"Rights: {model.metadata.rights}"),
                call(""),
                call("Input Parameters: "),
                call(self.mock_inputs_format_parameters.return_value),
                call(""),
                call("Input Data Slots: "),
                call(self.mock_inputs_format_dataslots.return_value),
                call(""),
                call("Outputs: "),
                call(self.mock_outputs_format_outputs.return_value),
            ],
        )
        mock_tabulate.assert_called_once_with(
            [
                ["Date:", format_datetime(model.creation_date, include_time=True)],
                ["ID:", model.model_id],
                ["Parent ID:", model.parent_id],
            ],
            tablefmt="plain",
        )
        mock_prose_print.assert_called_once_with("Test description", CONSOLE_WIDTH)

    @patch("dafni_cli.models.model.tabulate")
    @patch("dafni_cli.models.model.prose_print")
    @patch("dafni_cli.models.model.click")
    def test_output_details_correct_when_inputs_present_but_not_outputs(
        self, mock_click, mock_prose_print, mock_tabulate
    ):
        """Tests output_details works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)
        model.spec.outputs = None

        # CALL
        model.output_details()

        # ASSERT
        self.mock_inputs_format_parameters.assert_called_once()
        self.mock_inputs_format_dataslots.assert_called_once()
        self.mock_outputs_format_outputs.assert_not_called()
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"{model.metadata.display_name}  |  Status: {model.metadata.get_status_string()}  |  Tags: {', '.join(model.version_tags)}"
                ),
                call(""),
                call(f"Published by: {str(model.metadata.publisher)}"),
                call(
                    f"Contact Point: {model.metadata.contact_point_name} ({model.metadata.contact_point_email})"
                ),
                call(""),
                call(mock_tabulate.return_value),
                call(""),
                call("Version message:"),
                call(model.version_message),
                call(""),
                call("Summary:"),
                call(model.metadata.summary),
                call(""),
                call("Description:"),
                call(""),
                call("Source code:"),
                call(model.metadata.source_code),
                call(f"Licence: {model.metadata.licence}"),
                call(f"Rights: {model.metadata.rights}"),
                call(""),
                call("Input Parameters: "),
                call(self.mock_inputs_format_parameters.return_value),
                call(""),
                call("Input Data Slots: "),
                call(self.mock_inputs_format_dataslots.return_value),
            ]
        )
        mock_tabulate.assert_called_once_with(
            [
                ["Date:", format_datetime(model.creation_date, include_time=True)],
                ["ID:", model.model_id],
                ["Parent ID:", model.parent_id],
            ],
            tablefmt="plain",
        )
        mock_prose_print.assert_called_once_with("Test description", CONSOLE_WIDTH)

    @patch("dafni_cli.models.model.tabulate")
    @patch("dafni_cli.models.model.prose_print")
    @patch("dafni_cli.models.model.click")
    def test_output_details_correct_when_outputs_present_but_not_inputs(
        self, mock_click, mock_prose_print, mock_tabulate
    ):
        """Tests output_details works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)
        model.spec.inputs = None

        # CALL
        model.output_details()

        # ASSERT
        self.mock_inputs_format_parameters.assert_not_called()
        self.mock_inputs_format_dataslots.assert_not_called()
        self.mock_outputs_format_outputs.assert_called_once()
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(
                    f"{model.metadata.display_name}  |  Status: {model.metadata.get_status_string()}  |  Tags: {', '.join(model.version_tags)}"
                ),
                call(""),
                call(f"Published by: {str(model.metadata.publisher)}"),
                call(
                    f"Contact Point: {model.metadata.contact_point_name} ({model.metadata.contact_point_email})"
                ),
                call(""),
                call(mock_tabulate.return_value),
                call(""),
                call("Version message:"),
                call(model.version_message),
                call(""),
                call("Summary:"),
                call(model.metadata.summary),
                call(""),
                call("Description:"),
                call(""),
                call("Source code:"),
                call(model.metadata.source_code),
                call(f"Licence: {model.metadata.licence}"),
                call(f"Rights: {model.metadata.rights}"),
                call(""),
                call("Outputs: "),
                call(self.mock_outputs_format_outputs.return_value),
            ],
        )
        mock_tabulate.assert_called_once_with(
            [
                ["Date:", format_datetime(model.creation_date, include_time=True)],
                ["ID:", model.model_id],
                ["Parent ID:", model.parent_id],
            ],
            tablefmt="plain",
        )
        mock_prose_print.assert_called_once_with("Test description", CONSOLE_WIDTH)

    @patch("dafni_cli.models.model.tabulate")
    @patch("dafni_cli.models.model.prose_print")
    @patch("dafni_cli.models.model.click")
    def test_output_details_correct_when_neither_inputs_nor_outputs_are_present(
        self, mock_click, mock_prose_print, mock_tabulate
    ):
        """Tests output_details works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)
        model.spec.inputs = None
        model.spec.outputs = None

        # CALL
        model.output_details()

        # ASSERT
        self.mock_inputs_format_parameters.assert_not_called()
        self.mock_inputs_format_dataslots.assert_not_called()
        self.mock_outputs_format_outputs.assert_not_called()
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(
                    f"{model.metadata.display_name}  |  Status: {model.metadata.get_status_string()}  |  Tags: {', '.join(model.version_tags)}"
                ),
                call(""),
                call(f"Published by: {str(model.metadata.publisher)}"),
                call(
                    f"Contact Point: {model.metadata.contact_point_name} ({model.metadata.contact_point_email})"
                ),
                call(""),
                call(mock_tabulate.return_value),
                call(""),
                call("Version message:"),
                call(model.version_message),
                call(""),
                call("Summary:"),
                call(model.metadata.summary),
                call(""),
                call("Description:"),
                call(""),
                call("Source code:"),
                call(model.metadata.source_code),
                call(f"Licence: {model.metadata.licence}"),
                call(f"Rights: {model.metadata.rights}"),
            ],
        )
        mock_tabulate.assert_called_once_with(
            [
                ["Date:", format_datetime(model.creation_date, include_time=True)],
                ["ID:", model.model_id],
                ["Parent ID:", model.parent_id],
            ],
            tablefmt="plain",
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
            f"Name: Some display name\n"
            f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a\n"
            f"Publication date: {format_datetime(model.publication_date, include_time=True)}\n"
            "Version message: \n",
        )

    @patch("dafni_cli.models.model.format_table")
    @patch("dafni_cli.models.model.click")
    def test_output_version_history(self, mock_click, mock_format_table):
        """Tests output_version_history works correctly"""
        # SETUP
        model = parse_model(TEST_MODEL)

        # CALL
        model.output_version_history()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_VERSION_ID_HEADER,
                TABLE_PUBLICATION_DATE_HEADER,
                TABLE_VERSION_TAGS_HEADER,
                TABLE_VERSION_MESSAGE_HEADER,
            ],
            rows=[
                [
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                    format_datetime(datetime(2020, 4, 2, 9, 12, 25), include_time=True),
                    "latest",
                    "First version",
                ]
            ],
        )
        mock_click.echo.assert_called_once_with(mock_format_table.return_value)
