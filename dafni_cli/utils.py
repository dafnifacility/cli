from typing import List


def process_response_to_class_list(response: List[dict], class_instance: object):
    class_list = []
    for class_dict in response:
        instance = class_instance()
        instance.set_details_from_dict(class_dict)
        class_list.append(instance)
    return class_list