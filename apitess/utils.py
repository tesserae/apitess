"""Utility function shared by multiple endpoints"""
import urllib.parse

import flask
import tesserae.db.entities
from bson.objectid import ObjectId

import apitess.errors


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


def common_retrieve_status(db_find, results_id, search_type):
    results_status_found = db_find(tesserae.db.entities.Search.collection,
                                   results_id=results_id,
                                   search_type=search_type)
    if not results_status_found:
        response = flask.Response('Could not find results_id')
        response.status_code = 404
        return response
    status = results_status_found[0]
    response = flask.jsonify(results_id=status.results_id,
                             status=status.status,
                             message=status.msg,
                             progress=status.progress)
    if status.status != tesserae.db.entities.Search.DONE and \
            status.status != tesserae.db.entities.Search.FAILED:
        response.headers['Cache-Control'] = 'no-store'
    status.update_last_queried()
    flask.g.db.update(status)
    return response


def get_page_options_or_error(url_query_params):
    if len(url_query_params) == 0:
        return tesserae.utils.search.PageOptions(), None

    requireds = {'sort_by', 'sort_order', 'per_page', 'page_number'}
    potential_error = apitess.errors.check_requireds(url_query_params,
                                                     requireds)
    if potential_error:
        return None, potential_error
    allowed_sort_by = {'score', 'source_tag', 'target_tag', 'matched_features'}
    sort_by = url_query_params.get('sort_by')
    if sort_by not in allowed_sort_by:
        return None, apitess.errors.error(
            400,
            data=url_query_params,
            message=(
                f'Specified "sort_by" value ({sort_by}) is not supported. '
                f'(Supported values are {list(allowed_sort_by)})'))
    allowed_sort_order = {'ascending', 'descending'}
    sort_order = url_query_params.get('sort_order')
    if sort_order not in allowed_sort_order:
        return None, apitess.errors.error(
            400,
            data=url_query_params,
            message=(f'Specified "sort_order" value ({sort_order}) is not '
                     'supported. Supported values are '
                     f'{list(allowed_sort_order)})'))
    try:
        raw_per_page = url_query_params.get('per_page')
        per_page = int(raw_per_page)
    except ValueError:
        return None, apitess.errors.error(
            400,
            data=url_query_params,
            message=(f'Specified "per_page" value ({raw_per_page}) is not '
                     'supported. Only positive integers are supported.'))
    if per_page < 1:
        return None, apitess.errors.error(
            400,
            data=url_query_params,
            message=(f'Specified "per_page" value ({raw_per_page}) is not '
                     'supported. Only positive integers are supported.'))
    try:
        raw_page_number = url_query_params.get('page_number')
        page_number = int(raw_page_number)
    except ValueError:
        return None, apitess.errors.error(
            400,
            data=url_query_params,
            message=(
                f'Specified "page_number" value ({raw_page_number}) is '
                'not supported. Only non-negative integers are supported.'))
    if page_number < 0:
        return None, apitess.errors.error(
            400,
            data=url_query_params,
            message=(
                f'Specified "page_number" value ({raw_page_number}) is '
                'not supported. Only non-negative integers are supported.'))
    return tesserae.utils.search.PageOptions(sort_by=sort_by,
                                             sort_order=sort_order,
                                             per_page=per_page,
                                             page_number=page_number), None
