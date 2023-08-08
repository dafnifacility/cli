# Example auth dictionaries from either the model or workflow endpoints
TEST_AUTH_DATA_OBJECT: dict = {
    "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "view": True,
    "read": True,
    "update": False,
    "destroy": False,
    "reason": "Accessed as part of the Public group",
}

# Example auth dictionaries from either the models or workflows endpoints
TEST_AUTH_DATA_OBJECTS: dict = {
    "reason": "Accessed as part of the Public group",
    "role_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "name": "Executor",
    "view": True,
    "read": True,
    "update": False,
    "destroy": False,
    "description": "False",
}
