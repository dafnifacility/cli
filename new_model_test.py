from dafni_cli.api.models_api import get_model
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.api.session import DAFNISession
from dafni_cli.model.model import Model


session = DAFNISession()

data = get_model(
    session,
    "94e5726f-40f9-44d3-aa6b-70de18ae0bfe",
)
model: Model = ParserBaseObject.parse_from_dict(Model, data)
print(model.spec.outputs)
