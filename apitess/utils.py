"""Utility function shared by multiple endpoints"""
import urllib.parse

from bson.objectid import ObjectId


def fix_id(entity_json):
    """Replaces entity_json['id'] with entity_json['object_id']

    Note that this updates entity_json in place
    """
    entity_json['object_id'] = entity_json['id']
    del entity_json['id']
    return entity_json


def make_object_ids(ids):
    """Attempts to construct a list of ObjectIds

    Parameters
    ----------
    ids : list of str
        items to be turned into ObjectIds

    Returns
    -------
    results : list of ObjectId
        items that were successfully converted into ObjectIds
    failures : list of str
        items that failed to be converted into ObjectIds
    """
    results = []
    failures = []
    for item in ids:
        if ObjectId.is_valid(item):
            results.append(ObjectId(item))
        else:
            failures.append(item)
    return results, failures


def parse_commas(in_str):
    if ',' in in_str:
        return in_str.split(',')
    return [in_str]


def parse_works_arg(works):
    works = urllib.parse.unquote(works)
    works = parse_commas(works)
    oids, fails = make_object_ids(works)
    return oids, fails
