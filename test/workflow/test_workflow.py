from datetime import datetime
from typing import List
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.utils import format_datetime
from dafni_cli.workflow.instance import WorkflowInstance
from dafni_cli.workflow.parameter_set import WorkflowParameterSet
from dafni_cli.workflow.workflow import (
    Workflow,
    WorkflowVersion,
    parse_workflow,
    parse_workflows,
)

from test.fixtures.auth import TEST_AUTH_DATA_OBJECT, TEST_AUTH_DATA_OBJECTS
from test.workflow.test_instance import TEST_WORKFLOW_INSTANCE
from test.workflow.test_parameter_set import TEST_WORKFLOW_PARAMETER_SET

TEST_WORKFLOW_METADATA: dict = {
    "description": "Test workflow",
    "display_name": "A Workflow",
    "name": "test-workflow-name",
    "publisher": "Joel Davies",
    "summary": "Test workflow created to learn about DAFNI",
}

TEST_WORKFLOW_VERSION: dict = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "version_tags": ["latest"],
    "publication_date": "2023-04-04T08:34:36.531809Z",
    "version_message": "Initial Workflow version",
}

TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT: dict = {
    "auth": TEST_AUTH_DATA_OBJECTS,
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "kind": "W",
    "display_name": "A Workflow",
    "name": "test-workflow-name",
    "summary": "Test workflow created to learn about DAFNI",
    "creation_date": "2023-04-04T08:34:36.531809Z",
    "publication_date": "2023-04-04T08:34:36.531809Z",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "version_tags": [],
    "version_message": "",
    "parent": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "version_history": [TEST_WORKFLOW_VERSION],
}

TEST_WORKFLOWS: List[dict] = [TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT]

TEST_WORKFLOW: dict = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "metadata": TEST_WORKFLOW_METADATA,
    "version_history": [
        {
            "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "version_tags": ["latest"],
            "publication_date": "2023-04-04T08:34:36.531809Z",
            "version_message": "Initial Workflow version",
        }
    ],
    "auth": TEST_AUTH_DATA_OBJECT,
    "instances": [
        TEST_WORKFLOW_INSTANCE,
    ],
    "parameter_sets": [TEST_WORKFLOW_PARAMETER_SET],
    "api_version": "v1.0.2",
    "kind": "W",
    "creation_date": "2023-04-04T08:34:36.531809Z",
    "publication_date": "2023-04-04T08:34:36.531809Z",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "version_tags": ["latest"],
    "version_message": "Initial Workflow version",
    "spec": {
        "steps": {
            "0a0a0a0a-0a00-0a00-a000-0a0a0000000a": {
                "kind": "visualisation",
                "name": "pub-and-vis-1",
                "files": [
                    {
                        "step": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                        "paths": ["outputs/*"],
                    }
                ],
                "metadata": {
                    "in_step": {
                        "@type": "dcat:Dataset",
                        "geojson": {
                            "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [1.7689121033873, 58.6726008965827],
                                        [-6.22821033596556, 58.6726008965827],
                                        [-6.22821033596556, 49.9554136614383],
                                        [1.7689121033873, 49.9554136614383],
                                        [1.7689121033873, 58.6726008965827],
                                    ]
                                ],
                            },
                            "properties": {},
                        },
                        "@context": ["metadata-v1"],
                        "dct:title": "Sunshine levels between 1960 and 2016 - by Joel",
                        "dcat:theme": [],
                        "dct:rights": None,
                        "dct:created": "2023-04-04T08:34:36Z",
                        "dct:creator": [
                            {
                                "@id": "https://dafni.ac.uk/",
                                "@type": "foaf:Organization",
                                "foaf:name": "test",
                                "internalID": None,
                            }
                        ],
                        "dct:license": {
                            "@id": "https://creativecommons.org/licences/by/4.0/",
                            "@type": "LicenseDocument",
                            "rdfs:label": None,
                        },
                        "dct:spatial": {
                            "@id": "2648147",
                            "@type": "dct:Location",
                            "rdfs:label": "Great Britain, United Kingdom",
                        },
                        "dct:subject": "Environment",
                        "dcat:keyword": ["sunshine"],
                        "dct:language": "en",
                        "dct:publisher": {
                            "@id": None,
                            "@type": "foaf:Organization",
                            "foaf:name": None,
                            "internalID": None,
                        },
                        "dct:conformsTo": {
                            "@id": None,
                            "@type": "dct:Standard",
                            "label": None,
                        },
                        "dct:identifier": [],
                        "dct:description": "Monthly sunshine levels between 1960 and 2016 in the UK. Collected as part of UKCP9.",
                        "dct:PeriodOfTime": {
                            "type": "dct:PeriodOfTime",
                            "time:hasEnd": "Invalid date",
                            "time:hasBeginning": "1960-01-01",
                        },
                        "dcat:contactPoint": {
                            "@type": "vcard:Organization",
                            "vcard:fn": "Joel Davies",
                            "vcard:hasEmail": "joel.davies@stfc.ac.uk",
                        },
                        "dafni_version_note": "Initial Dataset version",
                        "dct:accrualPeriodicity": None,
                    }
                },
                "position": {"x": 466, "y": 50},
                "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000a"],
                "visualisation_title": "uk-climate-vis",
                "visualisation_builder": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                "visualisation_description": "Test visualisation",
            },
            "0a0a0a0a-0a00-0a00-a000-0a0a0000000b": {
                "kind": "model",
                "name": "uk-climate",
                "inputs": [],
                "position": {"x": 212, "y": 58},
                "dependencies": [],
                "model_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            },
        }
    },
    "parent": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
}


class TestWorkflowVersion(TestCase):
    """Tests the WorkflowVersion dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowVersion"""
        workflow_version: WorkflowVersion = ParserBaseObject.parse_from_dict(
            WorkflowVersion, TEST_WORKFLOW_VERSION
        )

        self.assertEqual(workflow_version.version_id, TEST_WORKFLOW_VERSION["id"])
        self.assertEqual(
            workflow_version.version_message, TEST_WORKFLOW_VERSION["version_message"]
        )
        self.assertEqual(
            workflow_version.version_tags, TEST_WORKFLOW_VERSION["version_tags"]
        )
        self.assertEqual(
            workflow_version.publication_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )


class TestWorkflow(TestCase):
    """Tests the Workflow dataclass"""

    def test_parse_workflows(self):
        """Tests parsing of a workflow using test data for the
        /workflows endpoint"""
        workflow: Workflow = parse_workflows(TEST_WORKFLOWS)[0]

        self.assertEqual(
            workflow.workflow_id, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["id"]
        )

        # WorkflowVersion (contents tested in TestWorkflowVersion)
        self.assertEqual(len(workflow.version_history), 1)
        self.assertEqual(type(workflow.version_history[0]), WorkflowVersion)

        # Auth (contents tested in TestAuth)
        self.assertEqual(type(workflow.auth), Auth)

        self.assertEqual(workflow.kind, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["kind"])
        self.assertEqual(
            workflow.creation_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow.publication_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow.owner_id, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["owner"]
        )
        self.assertEqual(
            workflow.version_tags, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["version_tags"]
        )
        self.assertEqual(
            workflow.version_message,
            TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["version_message"],
        )
        self.assertEqual(
            workflow.parent_id, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["parent"]
        )

        # WorkflowInstance's
        self.assertEqual(workflow.instances, None)

        # WorkflowParameterSet's
        self.assertEqual(workflow.parameter_sets, None)

        self.assertEqual(workflow.api_version, None)
        self.assertEqual(workflow.spec, None)

        # Ensure the metadata is correct
        self.assertEqual(
            workflow.metadata.display_name,
            TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["display_name"],
        )
        self.assertEqual(
            workflow.metadata.name, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["name"]
        )
        self.assertEqual(
            workflow.metadata.summary, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["summary"]
        )
        self.assertEqual(
            workflow.metadata.publisher_id,
            None,
        )
        self.assertEqual(
            workflow.metadata.description,
            None,
        )

    def test_parse_workflow(self):
        """Tests parsing of a workflow using test data for the
        /workflow/<version_id> endpoint"""
        workflow: Workflow = parse_workflow(TEST_WORKFLOW)

        self.assertEqual(workflow.workflow_id, TEST_WORKFLOW["id"])

        # WorkflowVersion (contents tested in TestWorkflowVersion)
        self.assertEqual(len(workflow.version_history), 1)
        self.assertEqual(type(workflow.version_history[0]), WorkflowVersion)

        # Auth (contents tested in TestAuth)
        self.assertEqual(type(workflow.auth), Auth)

        self.assertEqual(workflow.kind, TEST_WORKFLOW["kind"])
        self.assertEqual(
            workflow.creation_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow.publication_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(workflow.owner_id, TEST_WORKFLOW["owner"])
        self.assertEqual(workflow.version_tags, TEST_WORKFLOW["version_tags"])
        self.assertEqual(workflow.version_message, TEST_WORKFLOW["version_message"])
        self.assertEqual(workflow.parent_id, TEST_WORKFLOW["parent"])

        # WorkflowInstance's (contents tested in TestWorkflowInstance)
        self.assertEqual(len(workflow.instances), 1)
        self.assertEqual(type(workflow.instances[0]), WorkflowInstance)

        # WorkflowParameterSet's (contents tested in TestWorkflowInstance)
        self.assertEqual(len(workflow.parameter_sets), 1)
        self.assertEqual(type(workflow.parameter_sets[0]), WorkflowParameterSet)

        self.assertEqual(workflow.api_version, TEST_WORKFLOW["api_version"])
        self.assertEqual(workflow.spec, TEST_WORKFLOW["spec"])

        # Ensure the metadata is correct
        self.assertEqual(
            workflow.metadata.display_name, TEST_WORKFLOW_METADATA["display_name"]
        )
        self.assertEqual(workflow.metadata.name, TEST_WORKFLOW_METADATA["name"])
        self.assertEqual(workflow.metadata.summary, TEST_WORKFLOW_METADATA["summary"])
        self.assertEqual(
            workflow.metadata.publisher_id, TEST_WORKFLOW_METADATA["publisher"]
        )
        self.assertEqual(
            workflow.metadata.description, TEST_WORKFLOW_METADATA["description"]
        )

    def _test_filter_by_date(
        self, workflow: Workflow, key: str, date_str: str, expected_output: bool
    ):
        """Utility function to check a particular set of parameters to
        filter_by_date does what is expected"""
        self.assertEqual(workflow.filter_by_date(key, date_str), expected_output)

    def test_filter_by_date(self):
        """Tests filter_by_date works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # Creation date and publication date's are:
        # 2023-04-04T08:34:36.531809Z
        # 2023-04-04T08:34:36.531809Z

        # CALL

        # Before
        self._test_filter_by_date(workflow, "creation", datetime(2018, 5, 16), True)
        self._test_filter_by_date(workflow, "publication", datetime(2018, 5, 16), True)
        # Equal
        self._test_filter_by_date(workflow, "creation", datetime(2023, 4, 4), True)
        self._test_filter_by_date(workflow, "publication", datetime(2023, 4, 4), True)
        # After
        self._test_filter_by_date(workflow, "creation", datetime(2023, 4, 25), False)
        self._test_filter_by_date(workflow, "publication", datetime(2023, 4, 25), False)

    def test_filter_by_date_error(self):
        """Tests filter_by_date raises an error if the key is wrong"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        with self.assertRaises(KeyError):
            workflow.filter_by_date("key", datetime(2020, 12, 11))

    @patch("dafni_cli.workflow.workflow.click")
    def test_output_details(self, mock_click):
        """Tests output_details works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"Name: A Workflow{TAB_SPACE}"
                    f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
                    f"Created: {format_datetime(workflow.creation_date, include_time=True)}"
                ),
                call("Summary: Test workflow created to learn about DAFNI"),
                call(""),
            ]
        )

    @patch("dafni_cli.workflow.workflow.prose_print")
    @patch("dafni_cli.workflow.workflow.click")
    def test_output_details_with_long(self, mock_click, mock_prose_print):
        """Tests output_details works correctly when 'long' is set to True"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_details(long=True)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"Name: A Workflow{TAB_SPACE}"
                    f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
                    f"Created: {format_datetime(workflow.creation_date, include_time=True)}"
                ),
                call("Summary: Test workflow created to learn about DAFNI"),
                call("Description: "),
                call(""),
            ]
        )
        mock_prose_print.called_once_with("description", CONSOLE_WIDTH)

    @patch("dafni_cli.workflow.workflow.prose_print")
    @patch("dafni_cli.workflow.workflow.click")
    def test_output_info(self, mock_click, mock_prose_print):
        """Tests output_info works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        workflow.output_info()

        mock_click.echo.assert_has_calls(
            [
                call("Name: A Workflow"),
                call(
                    f"Created: {format_datetime(workflow.creation_date, include_time=True)}"
                ),
                call("Summary: "),
                call("Test workflow created to learn about DAFNI"),
            ]
        )
        mock_prose_print.assert_called_once_with("Test workflow", CONSOLE_WIDTH)

    def test_get_version_details(self):
        """Tests get_version_details works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        result = workflow.get_version_details()

        # ASSERT
        self.assertEqual(
            result,
            f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
            f"Name: A Workflow{TAB_SPACE}"
            f"Publication date: {format_datetime(workflow.publication_date, include_time=True)}{TAB_SPACE}"
            "Version message: Initial Workflow version",
        )

    @patch("dafni_cli.workflow.workflow.click")
    def test_output_version_history(self, mock_click):
        """Tests output_version_history works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_version_history()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"Name: A Workflow{TAB_SPACE}"
                    f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
                    f"Publication date: {format_datetime(workflow.publication_date, include_time=True)}"
                ),
                call("Version message: Initial Workflow version"),
                call("Version tags: latest"),
                call(""),
            ]
        )
