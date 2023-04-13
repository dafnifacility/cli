from dafni_cli.workflow.workflow import Workflow


class WorkflowParameterSet:
    """
    Contains parameter set data
    """

    def __init__(self, session: DAFNISession, latest_version: Workflow):
        if latest_version.id is None:
            raise ValueError("Workflow must have version_id property")
        elif (
            latest_version.version_tags is None
            or latest_version.publication_date is None
            or latest_version.metadata["display_name"] is None
            or latest_version.dictionary is None
            or latest_version.version_message is None
            or "version_history" not in latest_version.dictionary
        ):
            latest_version.get_attributes_from_id(session, latest_version.id)

        self.dictionary = latest_version.dictionary["parameter_sets"]
        if len(self.dictionary) > 1:
            for parameter_set_dict in self.dictionary[1:]:
                parameter_set = None
