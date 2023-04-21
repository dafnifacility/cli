from dataclasses import dataclass
from typing import List

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import get_all_workflows, get_workflow
from dafni_cli.workflow.workflow import Workflow


session = DAFNISession()

# data = get_workflow(
#     session,
#     "0ca2e905-a7c0-4824-a91a-41d16238c1d6",  # Mine
#     # "cfb164b2-59de-4156-85ea-36049e147322",  # Test
# )
# workflow: Workflow = ParserBaseObject.parse_from_dict(Workflow, data)
# print(workflow.spec)


# data = get_all_workflows(
#     session,
# )
# print(data[0])


# data = get_all_workflows(session)
# workflow: Workflow = ParserBaseObject.parse_from_dict(Workflow, data[0])
# print(workflow)


data = get_all_workflows(session)
workflows: List[Workflow] = ParserBaseObject.parse_from_dict_list(Workflow, data)
print(workflows[0])
