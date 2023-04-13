import pytest
from mock import call, patch

from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.datasets.dataset_metadata import DataFile, DatasetMetadata

from test.fixtures.dataset_fixtures import (
    datafile_mock,
    dataset_meta_mock,
    dataset_metadata_fixture,
)
from test.fixtures.jwt_fixtures import JWT


class TestDataFile:
    """Test class to test the DataFile Class"""

    @patch.object(DataFile, "set_attributes_from_dict")
    class TestInit:
        """Test class to test the DataFile constructor"""

        def test_datafile_has_expected_attributes(self, mock_set):
            # SETUP
            expected_attr = ["name", "size", "format", "download", "contents"]
            # CALL
            instance = DataFile()
            # ASSERT
            assert all(getattr(instance, attr) is None for attr in expected_attr)

        def test_set_attributes_from_dict_called_if_given_a_dict(self, mock_set):
            # SETUP
            file_dict = {"key": "value"}
            # CALL
            DataFile(file_dict)
            # ASSERT
            mock_set.assert_called_once_with(file_dict)

    @patch("dafni_cli.datasets.dataset_metadata.process_file_size")
    @patch("dafni_cli.datasets.dataset_metadata.check_key_in_dict")
    class TestSetDetailsFromDict:
        """Test class to test the DataFile.init functionality"""

        def test_attributes_set_correctly(self, mock_check, mock_process):
            # SETUP
            mock_check.side_effect = (
                "Mock Check",
                "Size Mock",
                "Mock Format",
                "Mock download",
            )
            mock_process.return_value = "Mock Size"

            file_dict = {"key": "value"}
            instance = DataFile()

            # CALL
            instance.set_attributes_from_dict(file_dict)

            # ASSERT
            print(mock_process.call_args_list)
            assert instance.name == "Mock Check"
            assert instance.size == "Mock Size"
            assert instance.format == ""
            assert instance.download == "Mock download"
            assert instance.contents == None

        def test_util_functions_called_correctly(self, mock_check, mock_process):
            # SETUP
            mock_check.return_value = "Mock Check"
            mock_process.return_value = "Mock Size"

            file_dict = {"key": "value"}
            instance = DataFile()

            # CALL
            instance.set_attributes_from_dict(file_dict)

            # ASSERT
            assert mock_check.call_args_list == [
                call(file_dict, ["spdx:fileName"]),
                call(file_dict, ["dcat:byteSize"], default=None),
                call(file_dict, ["dcat:mediaType"]),
                call(file_dict, ["dcat:downloadURL"], default=None),
            ]
            mock_process.assert_called_once_with("Mock Check")

        @pytest.mark.parametrize(
            "file_format, expected",
            [
                ("application/octet-stream", "Binary"),
                ("application/pdf", "PDF"),
                ("application/vnd.ms-excel", "Excel"),
                (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "Excel",
                ),
                ("application/zip", "ZIP"),
                ("text/csv", "CSV"),
                ("text/plain", "Text"),
            ],
        )
        def test_format_mapped_correctly(
            self, mock_check, mock_process, file_format, expected
        ):
            # SETUP
            mock_check.side_effect = ("mock name", "mock size", file_format, "url")
            mock_process.return_value = "Mock Size"

            file_dict = {"key": "value"}
            instance = DataFile()

            # CALL
            instance.set_attributes_from_dict(file_dict)

            # ASSERT
            assert instance.format == expected

    @patch("dafni_cli.datasets.dataset_metadata.dafni_get_request")
    class TestDownloadContents:
        """test class to test the download_contents functionality"""

        def test_contents_set_to_returned_file_contents(self, mock_get):
            # SETUP
            contents = b"Test data"
            mock_get.return_value = contents

            instance = DataFile()
            instance.download = "download/url"

            jwt = JWT

            # CALL
            instance.download_contents(jwt)

            # ASSERT
            mock_get.assert_called_once_with(instance.download, jwt, content=True)

            assert contents == instance.contents.getvalue()


class TestDatasetMeta:
    """Test class for the DatasetMetadata class"""

    class TestInit:
        """Test class for the DatasetMetadata.__init__() function"""

        def test_the_correct_attributes_are_created(self):
            # SETUP
            none_keys = [
                "created",
                "creator",
                "contact",
                "description",
                "identifier",
                "location",
                "start_date",
                "end_date",
                "themes",
                "publisher",
                "issued",
                "rights",
                "language",
                "standard",
                "update",
                "title",
                "dataset_id",
                "version_id",
            ]
            array_keys = ["files", "keywords"]

            # CALL
            instance = DatasetMetadata()

            # ASSERT
            assert all(getattr(instance, key) is None for key in none_keys)
            assert all(getattr(instance, key) == [] for key in array_keys)

        @patch.object(DatasetMetadata, "set_attributes_from_dict")
        def test_set_attributes_from_dict_called_if_give_dict(self, mock_set):
            # SETUP
            dataset_dict = {"key": "value"}
            # CALL
            DatasetMetadata(dataset_dict)
            # ASSERT
            mock_set.assert_called_once_with(dataset_dict)

    class TestSetDetailsFromDict:
        """Test class to test the set_attributes_from_dict functionality"""

        @patch.object(DataFile, "__init__")
        @patch("dafni_cli.datasets.dataset_metadata.check_key_in_dict")
        @patch("dafni_cli.datasets.dataset_metadata.process_dict_datetime")
        def test_helper_functions_called_correctly_when_files_available(
            self, mock_date, mock_dict, mock_datafile
        ):
            # SETUP
            mock_datafile.return_value = None
            mock_date.side_effect = ("Created", "Start date", "End date", "Issued")
            mock_dict.side_effect = (
                "Creator",
                "Contact",
                "Description",
                "Identifier",
                "Location",
                "Keywords",
                "Files",
                "Themes",
                "Publisher",
                "Rights",
                "Language",
                "Standard",
                "Update",
                "ID",
                "Title",
                "Version_ID",
            )

            instance = DatasetMetadata()
            dataset_dict = {
                "dcat:distribution": [{"key": "value"}],
                "dct:creator": [{"foaf:name": "Name"}],
            }

            # CALL
            instance.set_attributes_from_dict(dataset_dict)

            # ASSERT
            assert mock_date.call_args_list == [
                call(dataset_dict, ["dct:created"]),
                call(dataset_dict, ["dct:PeriodOfTime", "time:hasBeginning"]),
                call(dataset_dict, ["dct:PeriodOfTime", "time:hasEnd"]),
                call(dataset_dict, ["dct:issued"]),
            ]
            assert mock_dict.call_args_list == [
                call(dataset_dict, ["dct:creator"], default=None),
                call(dataset_dict, ["dcat:contactPoint", "vcard:hasEmail"]),
                call(dataset_dict, ["dct:description"]),
                call(dataset_dict, ["dct:identifier"]),
                call(dataset_dict, ["dct:spatial", "rdfs:label"]),
                call(dataset_dict, ["dcat:keyword"]),
                call(dataset_dict, ["dcat:distribution"], default=None),
                call(dataset_dict, ["dcat:theme"]),
                call(dataset_dict, ["dct:publisher", "foaf:name"]),
                call(dataset_dict, ["dct:rights"]),
                call(dataset_dict, ["dct:language"]),
                call(dataset_dict, ["dct:conformsTo", "label"]),
                call(dataset_dict, ["dct:accrualPeriodicity"]),
                call(dataset_dict, ["@id", "dataset_uuid"]),
                call(dataset_dict, ["dct:title"]),
                call(dataset_dict, ["@id", "version_uuid"]),
            ]

            mock_datafile.assert_called_once_with({"key": "value"})

        @patch.object(DataFile, "__init__")
        @patch("dafni_cli.datasets.dataset_metadata.check_key_in_dict")
        @patch("dafni_cli.datasets.dataset_metadata.process_dict_datetime")
        def test_helper_functions_called_correctly_when_no_files_available(
            self, mock_date, mock_dict, mock_datafile
        ):
            # SETUP
            mock_datafile.return_value = None
            mock_date.side_effect = ("Created", "Start date", "End date", "Issued")
            mock_dict.side_effect = (
                "Creator",
                "Contact",
                "Description",
                "Identifier",
                "Location",
                "Keywords",
                None,
                "Themes",
                "Publisher",
                "Rights",
                "Language",
                "Standard",
                "Update",
                "ID",
                "Title",
                ["Versions"],
                "Version_IDs",
            )

            instance = DatasetMetadata()
            dataset_dict = {
                "dcat:distribution": [{"key": "value"}],
                "dct:creator": [{"foaf:name": "Name"}],
            }

            # CALL
            instance.set_attributes_from_dict(dataset_dict)

            # ASSERT
            mock_datafile.assert_not_called()

        def test_set_attributes_from_dict_sets_attributes_correctly(
            self, dataset_metadata_fixture
        ):
            # SETUP
            dataset_dict = dataset_metadata_fixture
            instance = DatasetMetadata()

            # CALL
            instance.set_attributes_from_dict(dataset_dict)

            # ASSERT
            assert instance.created == "March 16 2021"
            assert instance.creator == dataset_dict["dct:creator"][0]["foaf:name"]
            assert (
                instance.contact == dataset_dict["dcat:contactPoint"]["vcard:hasEmail"]
            )
            assert instance.description == dataset_dict["dct:description"]
            assert instance.identifier == dataset_dict["dct:identifier"]
            assert instance.location == dataset_dict["dct:spatial"]["rdfs:label"]
            assert instance.start_date == "March 27 2019"
            assert instance.end_date == "March 27 2021"
            assert instance.keywords == dataset_dict["dcat:keyword"]
            assert all(isinstance(datafile, DataFile) for datafile in instance.files)
            assert instance.themes == dataset_dict["dcat:theme"]
            assert instance.publisher == dataset_dict["dct:publisher"]["foaf:name"]
            assert instance.issued == "March 16 2021"
            assert instance.rights == dataset_dict["dct:rights"]
            assert instance.language == dataset_dict["dct:language"]
            assert instance.standard == dataset_dict["dct:conformsTo"]["label"]
            assert instance.update == dataset_dict["dct:accrualPeriodicity"]

    @patch.object(DatasetMetadata, "output_metadata_extra_details")
    @patch.object(DatasetMetadata, "output_datafiles_table")
    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    class TestOutputMetadataDetails:
        """Test class to test the output_metadata_details functionality"""

        def test_data_outputted_as_expected(
            self, mock_click, mock_prose, mock_table, mock_extra
        ):
            # SETUP
            instance = dataset_meta_mock()

            # CALL
            instance.output_metadata_details()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(f"\nCreated: {instance.created}"),
                call(f"Creator: {instance.creator}"),
                call(f"Contact: {instance.contact}"),
                call("Description:"),
                call("Identifier: "),
                call(f"Location: {instance.location}"),
                call(f"Start date: {instance.start_date}"),
                call(f"End date: {instance.end_date}"),
                call(f"Key Words:\n {instance.keywords}"),
            ]
            assert mock_prose.call_args_list == [
                call(instance.description, CONSOLE_WIDTH),
                call(" ".join(instance.identifier), CONSOLE_WIDTH),
            ]

            assert mock_table.call_args_list == [call()]
            mock_extra.assert_not_called()

        def test_output_metadata_extra_details_called_if_long_set_to_true(
            self,
            mock_click,
            mock_prose,
            mock_table,
            mock_extra,
        ):
            # SETUP
            instance = dataset_meta_mock()

            # CALL
            instance.output_metadata_details(long=True)

            # ASSERT
            mock_extra.assert_called_once()

    @patch("dafni_cli.datasets.dataset_metadata.output_table")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    class TestOutputDatafilesTable:
        """Test class to test the DatasetMetadata.output_datafiles_table() functionality"""

        @pytest.mark.parametrize("width", range(6, 50, 5))
        @pytest.mark.parametrize(
            "files",
            [["1", "2_", "_3_", "__4_", "__5__"], []],
            ids=["Multiple files", "1 File"],
        )
        def test_output_table_called_with_correct_values(
            self, mock_click, mock_output, width, files
        ):
            # SETUP
            # setup datafiles
            name_str = "T"
            file_name = f"{name_str:{width}}"
            files.append(file_name)

            instance_files = [datafile_mock(name=name) for name in files]
            instance = DatasetMetadata()
            instance.files = instance_files

            # CALL
            instance.output_datafiles_table()

            # ASSERT
            columns = ["Name", "Size", "Format"]
            widths = [width, 10, 6]
            rows = [
                [datafile.name, datafile.size, datafile.format]
                for datafile in instance_files
            ]
            mock_output.assert_called_once_with(columns, widths, rows)

        def test_click_echo_called_with_correct_values(self, mock_click, mock_output):
            # SETUP
            # setup datafiles
            instance_files = [datafile_mock()]
            instance = DatasetMetadata()
            instance.files = instance_files
            # setup output table
            mock_output.return_value = "output table"

            # CALL
            instance.output_datafiles_table()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call("\nData Files"),
                call("output table"),
            ]

    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    class TestOutputMetadataExtraDetails:
        """Test class to test DatasetMetadata.output_metadata_extra_details()"""

        def test_extra_details_outputted_as_expected(self, mock_click, mock_prose):
            # SETUP
            instance = dataset_meta_mock()

            # CALL
            instance.output_metadata_extra_details()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(f"Themes:\n{instance.themes}"),
                call(f"Publisher: {instance.publisher}"),
                call(f"Issued: {instance.issued}"),
                call("Rights:"),
                call(f"Language: {instance.language}"),
                call(f"Standard: {instance.standard}"),
                call(f"Update Frequency: {instance.update}"),
            ]

            mock_prose.assert_called_once_with(instance.rights, CONSOLE_WIDTH)

    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    class TestOutputVersionDetails:
        """Test class to test DatasetMetadata.output_version_details()"""

        def test_version_details_outputted_as_expected(self, mock_click, mock_prose):
            # SETUP
            instance = dataset_meta_mock()

            # CALL
            instance.output_version_details()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(f"\nTitle: {instance.title}"),
                call(f"ID: {instance.dataset_id}"),
                call(f"Version ID: {instance.version_id}"),
                call(f"Publisher: {instance.publisher}"),
                call(f"From: {instance.start_date}{TAB_SPACE}To: {instance.end_date}"),
                call("Description: "),
            ]

            mock_prose.assert_called_once_with(instance.description, CONSOLE_WIDTH)

    @patch.object(DataFile, "download_contents")
    class TestDownloadDatasetFiles:
        """test class to test the download_dataset_files functionality"""

        def test_empty_arrays_returned_if_dataset_has_no_associated_files(
            self, mock_download
        ):
            # SETUP
            instance = DatasetMetadata()
            instance.files = []

            jwt = JWT

            # CALL
            file_names, file_contents = instance.download_dataset_files(jwt)

            # ASSERT
            mock_download.assert_not_called()

            assert file_names == []
            assert file_contents == []

        def test_correct_names_and_contents_returned_if_dataset_has_associated_files(
            self, mock_download
        ):
            # SETUP
            instance = DatasetMetadata()
            data_file_1 = datafile_mock()
            data_file_2 = datafile_mock(name="File 2", contents=b"Test Data 2")

            instance.files = [data_file_1, data_file_2]

            jwt = JWT

            # CALL
            file_names, file_contents = instance.download_dataset_files(jwt)

            # ASSERT
            assert mock_download.call_args_list == [call(jwt), call(jwt)]

            assert file_names == [data_file_1.name, data_file_2.name]
            assert file_contents == [data_file_1.contents, data_file_2.contents]
