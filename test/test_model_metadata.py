from dafni_cli.model import model_metadata
from mock import patch

from test.fixtures.model_fixtures import get_model_metadata_fixture
from dafni_cli.consts import (
    INPUT_TITLE_HEADER,
    INPUT_TYPE_HEADER,
    INPUT_MIN_HEADER,
    INPUT_MAX_HEADER,
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_TYPE_COLUMN_WIDTH,
    INPUT_MIN_MAX_COLUMN_WIDTH,
    INPUT_DESCRIPTION_LINE_WIDTH,
    OUTPUT_FORMAT_COLUMN_WIDTH,
    OUTPUT_SUMMARY_COLUMN_WIDTH,
    OUTPUT_NAME_HEADER,
    OUTPUT_FORMAT_HEADER,
    OUTPUT_SUMMARY_HEADER,
    TAB_SPACE,
)


class TestParamsTableHeader:
    """Test class for the params_table_header functionality"""

    def test_header_row_is_formatted_properly(self):
        # SETUP
        title_column_width = 10
        default_column_width = 10
        # Expected headings string
        expected = (
            INPUT_TITLE_HEADER
            + " " * (title_column_width - len(INPUT_TITLE_HEADER))
            + INPUT_TYPE_HEADER
            + " " * (INPUT_TYPE_COLUMN_WIDTH - len(INPUT_TYPE_HEADER))
            + INPUT_MIN_HEADER
            + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - len(INPUT_MIN_HEADER))
            + INPUT_MAX_HEADER
            + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - len(INPUT_MAX_HEADER))
            + INPUT_DEFAULT_HEADER
            + " " * (default_column_width - len(INPUT_DEFAULT_HEADER))
            + INPUT_DESCRIPTION_HEADER
        )

        # CALL
        header_string = model_metadata.params_table_header(
            title_column_width, default_column_width
        )

        # ASSERT
        assert header_string.split("\n")[0] == expected

    def test_dashed_line_is_of_expected_length(self):
        # SETUP
        title_column_width = 10
        default_column_width = 10
        # Expected headings string
        expected = "-" * (
            title_column_width
            + INPUT_TYPE_COLUMN_WIDTH
            + 2 * INPUT_MIN_MAX_COLUMN_WIDTH
            + default_column_width
            + INPUT_DESCRIPTION_LINE_WIDTH
        )

        # CALL
        header_string = model_metadata.params_table_header(
            title_column_width, default_column_width
        )

        # ASSERT
        assert header_string.split("\n")[1] == expected


class TestOutputsTableHeader:
    """Test class for the outputs_table_header functionality"""

    def test_header_row_is_formatted_properly(self):
        # SETUP
        name_column_width = 10
        # Expected headings string
        expected = (
            OUTPUT_NAME_HEADER
            + " " * (name_column_width - len(OUTPUT_NAME_HEADER))
            + OUTPUT_FORMAT_HEADER
            + " " * (OUTPUT_FORMAT_COLUMN_WIDTH - len(OUTPUT_FORMAT_HEADER))
            + OUTPUT_SUMMARY_HEADER
        )

        # CALL
        header_string = model_metadata.outputs_table_header(name_column_width)

        # ASSERT
        assert header_string.split("\n")[0] == expected

    def test_dashed_line_is_of_expected_length(self):
        # SETUP
        name_column_width = 10
        # Expected headings string
        expected = "-" * (
            name_column_width + OUTPUT_FORMAT_COLUMN_WIDTH + OUTPUT_SUMMARY_COLUMN_WIDTH
        )

        # CALL
        header_string = model_metadata.outputs_table_header(name_column_width)

        # ASSERT
        assert header_string.split("\n")[1] == expected


class TestModelMetadata:
    """Test class for the Model class"""

    class TestInit:
        """Test class to test the ModelMetadata.__init__() functionality"""

        def test_expected_attributes_found_on_class(self, get_model_metadata_fixture):
            # SETUP
            expected_attributes = ["dictionary", "inputs", "outputs", "owner"]
            metadata_dict = get_model_metadata_fixture

            # CALL
            instance = model_metadata.ModelMetadata(metadata_dict)
            # ASSERT
            assert isinstance(instance, model_metadata.ModelMetadata)
            assert all(
                getattr(instance, value) is not None for value in expected_attributes
            )

        def test_attributes_have_expected_values(self, get_model_metadata_fixture):
            # SETUP
            metadata_dict = get_model_metadata_fixture

            # CALL
            instance = model_metadata.ModelMetadata(metadata_dict)

            # ASSERT
            assert instance.dictionary == metadata_dict
            assert instance.inputs == metadata_dict["spec"]["inputs"]
            assert instance.outputs == metadata_dict["spec"]["outputs"]
            assert instance.owner == metadata_dict["metadata"]["owner"]

        def test_attributes_have_expected_values_when_inputs_and_outputs_missing(
            self, get_model_metadata_fixture
        ):
            # SETUP
            metadata_dict = get_model_metadata_fixture
            del metadata_dict["spec"]["outputs"]
            del metadata_dict["spec"]["inputs"]

            # CALL
            instance = model_metadata.ModelMetadata(metadata_dict)

            # ASSERT
            assert instance.dictionary == metadata_dict
            assert instance.inputs is None
            assert instance.outputs is None
            assert instance.owner == metadata_dict["metadata"]["owner"]

        @patch("dafni_cli.model_metadata.params_table_header")
        @patch("dafni_cli.model_metadata.optional_column")
        class TestFormatParameters:
            """Test class to test the ModelMetadata.format_parameters() functionality"""

            def test_paramaters_table_is_formatted_properly(
                self, mock_column, mock_header, get_model_metadata_fixture
            ):
                # SETUP
                metadata_dict = get_model_metadata_fixture
                metadata = model_metadata.ModelMetadata(metadata_dict)
                # Ignore table header
                mock_header.return_value = ""
                # Setup optional column return values
                optional_column_outputs = [
                    f"0.1" + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - 3),
                    f"2.0" + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - 3),
                    f"1.5" + " " * 16,
                    " " * INPUT_MIN_MAX_COLUMN_WIDTH,
                    " " * INPUT_MIN_MAX_COLUMN_WIDTH,
                    "long_default_name" + " " * 2,
                ]
                mock_column.side_effect = optional_column_outputs
                # Expected table
                expected_table = (
                    f"R Number"
                    + " " * 2
                    + f"number"
                    + " " * (INPUT_TYPE_COLUMN_WIDTH - 6)
                    + optional_column_outputs[0]
                    + optional_column_outputs[1]
                    + optional_column_outputs[2]
                    + f"The reproduction number\n"
                    + f"Setting"
                    + " " * 3
                    + f"string"
                    + " " * (INPUT_TYPE_COLUMN_WIDTH - 6)
                    + optional_column_outputs[3]
                    + optional_column_outputs[4]
                    + optional_column_outputs[5]
                    + "Mode to run the model in\n"
                )
                # CALL
                table_string = metadata.format_parameters()

                # ASSERT
                assert expected_table == table_string

        class TestFormatDataslots:
            """Test class to test the ModelMetadata.format_dataslots() functionality"""

            def test_dataslots_is_formatted_properly(self, get_model_metadata_fixture):
                # SETUP
                metadata_dict = get_model_metadata_fixture
                metadata = model_metadata.ModelMetadata(metadata_dict)
                # Expected output
                expected = (
                    f"Name: Inputs\n"
                    + f"Path in container: inputs/\n"
                    + f"Required: True\n"
                    + f"Default Datasets: \n"
                    + f"Name: "
                    + f"ID: 11111a1a-a111-11aa-a111-11aa11111aaa"
                    + TAB_SPACE
                    + f"Version ID: 21111a1a-a111-11aa-a111-11aa11111aaa"
                    + TAB_SPACE
                    + "\n"
                )

                # CALL
                dataslot_string = metadata.format_dataslots()

                # ASSERT
                assert dataslot_string == expected

        @patch("dafni_cli.model_metadata.outputs_table_header")
        @patch("dafni_cli.model_metadata.optional_column")
        class TestFormatOutputs:
            """Test class to test the ModelMetadata.format_outputs() functionality"""

            def test_outputs_table_is_formatted_properly(
                self, mock_column, mock_header, get_model_metadata_fixture
            ):
                # SETUP
                metadata_dict = get_model_metadata_fixture
                metadata = model_metadata.ModelMetadata(metadata_dict)
                # Ignore table header
                mock_header.return_value = ""
                # Setup optional column return values
                optional_column_outputs = [
                    "Dataset 1 description",
                    "Dataset 2 description",
                ]
                mock_column.side_effect = optional_column_outputs
                # Expected table
                expected_table = (
                    f"dataset_1.xls"
                    + " " * 2
                    + f"xls"
                    + " " * (OUTPUT_FORMAT_COLUMN_WIDTH - 3)
                    + optional_column_outputs[0]
                    + "\n"
                    + f"dataset_2.xls"
                    + " " * 2
                    + f"xls"
                    + " " * (INPUT_TYPE_COLUMN_WIDTH - 3)
                    + optional_column_outputs[1]
                    + "\n"
                )
                # CALL
                table_string = metadata.format_outputs()

                # ASSERT
                assert expected_table == table_string
