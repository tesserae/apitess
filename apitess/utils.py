"""Utility function shared by multiple endpoints"""


def fix_id(entity_json):
    """Replaces entity_json['id'] with entity_json['object_id']

    Note that this updates entity_json in place
    """
    entity_json['object_id'] = entity_json['id']
    del entity_json['id']
    return entity_json
