import time
from typing import List

from dafni_cli.api.models_api import get_all_models, get_model
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.api.session import DAFNISession
from dafni_cli.model.model import Model

session = DAFNISession()

# data = get_model(
#     session,
#     "94e5726f-40f9-44d3-aa6b-70de18ae0bfe",  # Mine
#     # "9de4ad50-fd98-4def-9bfc-39378854e6a1",  # Test
# )
# model: Model = ParserBaseObject.parse_from_dict(Model, data)
# print(model)

# data = get_all_models(session)

# model: Model = ParserBaseObject.parse_from_dict(Model, data[0])
# print(model)


# This gives:
# Getting models:  6.3229920864105225
# Parsing models:  0.02218008041381836
# start_t = time.time()
# data = get_all_models(session)
# print("Getting models: ", time.time() - start_t)
# start_t = time.time()
# models: List[Model] = ParserBaseObject.parse_from_dict_list(Model, data)
# print("Parsing models: ", time.time() - start_t)


data = get_all_models(session)
models: List[Model] = ParserBaseObject.parse_from_dict_list(Model, data)
print(models[0].metadata)
