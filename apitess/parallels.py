"""The family of /parallels/ endpoints"""
import gzip
import os
import queue
import uuid

from bson.objectid import ObjectId
import flask
from flask_cors import cross_origin

import tesserae.db.entities
from tesserae.matchers.text_options import TextOptions
import tesserae.utils.search
import apitess.errors
from apitess.utils import common_retrieve_status

bp = flask.Blueprint('parallels', __name__, url_prefix='/parallels')


def _validate_units(specs, name):
    """Provide error messages if units are not specified correctly

    Parameters
    ----------
    specs : dict
        specification of which units from what text
    name : str
        either 'source' or 'target'

    Returns
    -------
    list of str
        error messages corresponding to errors encountered
    """
    result = []
    if 'object_id' not in specs:
        result.append('{} is missing object_id.'.format(name))
    if 'units' not in specs:
        result.append('{} is missing units.'.format(name))
    else:
        units = specs['units']
        if units != 'line' and units != 'phrase':
            result.append('{} has unrecognized units: {}'.format(name, units))
    return result


@bp.route('/', methods=('POST', 'OPTIONS',))
@cross_origin(expose_headers='Location')
def submit_search():
    """Run a Tesserae search"""
    received = flask.request.get_json()
    requireds = {'source', 'target', 'method'}
    miss_error = apitess.errors.check_requireds(received, requireds)
    if miss_error:
        return miss_error

    source = received['source']
    target = received['target']

    errors = _validate_units(source, 'source')
    errors.extend(_validate_units(target, 'target'))
    if errors:
        return apitess.errors.error(
            400,
            data=received,
            message=('The following errors were found in source and target '
                     'unit specifications:\n{}'.format('\n\t'.join(errors))))

    source_object_id = source['object_id']
    target_object_id = target['object_id']
    results = flask.g.db.find(
        tesserae.db.entities.Text.collection,
        _id=[ObjectId(source_object_id), ObjectId(target_object_id)])
    results = {str(t.id): t for t in results}
    errors = []
    if source_object_id not in results:
        errors.append(source_object_id)
    if target_object_id not in results:
        errors.append(target_object_id)
    if errors:
        return apitess.errors.error(
            400,
            data=received,
            message=('Unable to find the following object_id(s) among the '
                     'texts in the database:\n\t{}'.format(
                         '\n\t'.join(errors))))
    source_text = results[source_object_id]
    target_text = results[target_object_id]

    method_requireds = {
        'original': {
            'name', 'feature', 'stopwords', 'freq_basis', 'max_distance',
            'distance_basis'
        }
    }
    method = received['method']
    if 'name' not in method:
        return apitess.errors.error(
            400,
            data=received,
            message='No specified method name.')
    missing = []
    for req in method_requireds[method['name']]:
        if req not in method:
            missing.append(req)
    if missing:
        return apitess.errors.error(
            400,
            data=received,
            message=('The specified method is missing the following required '
                     'key(s): {}'.format(', '.join(missing))))

    results_id = tesserae.utils.search.check_cache(
        flask.g.db, source, target, method)
    if results_id:
        response = flask.Response()
        response.status_code = 303
        response.status = '303 See Other'
        # we want the final '/' on the URL
        response.headers['Location'] = os.path.join(
                flask.request.base_url, results_id, '')
        return response

    response = flask.Response()
    response.status_code = 201
    response.status = '201 Created'
    results_id = uuid.uuid4().hex
    # we want the final '/' on the URL
    response.headers['Location'] = os.path.join(
        flask.request.base_url, results_id, '')

    try:
        tesserae.utils.search.submit_search(
            flask.g.jobqueue, results_id, method['name'], {
                'source': TextOptions(source_text, source['units']),
                'target': TextOptions(target_text, target['units']),
                'feature': method['feature'],
                'stopwords': method['stopwords'],
                'freq_basis': method['freq_basis'],
                'max_distance': method['max_distance'],
                'distance_basis': method['distance_basis'],
                'min_score': 0
            })
    except queue.Full:
        return apitess.error.error(
            500,
            data=received,
            message=('The search request could not be added to the queue. '
                     'Please try again in a few minutes'))
    return response


@bp.route('/<results_id>/status/')
@cross_origin()
def retrieve_status(results_id):
    return common_retrieve_status(
        flask.g.db.find,
        results_id,
        tesserae.utils.search.NORMAL_SEARCH
    )


@bp.route('/<results_id>/')
@cross_origin()
def retrieve_results(results_id):
    # get search results
    results_status_found = flask.g.db.find(
        tesserae.db.entities.Search.collection,
        results_id=results_id,
        search_type=tesserae.utils.search.NORMAL_SEARCH
    )
    if not results_status_found:
        response = flask.Response('Could not find results_id')
        response.status_code = 404
        return response
    if results_status_found[0].status != tesserae.db.entities.Search.DONE:
        status_url = os.path.join(
            flask.request.base_url, results_id, 'status', '')
        response = flask.Response(
            f'Unable to retrieve results; check {status_url} endpoint.')
        response.headers['Cache-Control'] = 'no-store'
        response.status_code = 404
        return response

    params = results_status_found[0].parameters
    url_query_params = flask.request.args
    if len(url_query_params) == 0:
        page_options = tesserae.utils.search.PageOptions()
    else:
        requireds = {
            'sort_by',
            'sort_order',
            'per_page',
            'page_number'
        }
        potential_error = apitess.errors.check_requireds(url_query_params,
                                                         requireds)
        if potential_error:
            return potential_error
        allowed_sort_by = {
            'score',
            'source_tag',
            'target_tag',
            'matched_features'
        }
        sort_by = url_query_params.get('sort_by')
        if sort_by not in allowed_sort_by:
            return apitess.errors.error(
                400,
                data=url_query_params,
                message=(
                    f'Specified "sort_by" value ({sort_by}) is not supported. '
                    f'(Supported values are {list(allowed_sort_by)})'
                )
            )
        allowed_sort_order = {
            'ascending',
            'descending'
        }
        sort_order = url_query_params.get('sort_order')
        if sort_order not in allowed_sort_order:
            return apitess.errors.error(
                400,
                data=url_query_params,
                message=(
                    f'Specified "sort_order" value ({sort_order}) is not '
                    'supported. Supported values are '
                    f'{list(allowed_sort_order)})'
                )
            )
        try:
            raw_per_page = url_query_params.get('per_page')
            per_page = int(raw_per_page)
        except ValueError:
            return apitess.errors.error(
                400,
                data=url_query_params,
                message=(
                    f'Specified "per_page" value ({raw_per_page}) is not '
                    'supported. Only positive integers are supported.'
                )
            )
        if per_page < 1:
            return apitess.errors.error(
                400,
                data=url_query_params,
                message=(
                    f'Specified "per_page" value ({raw_per_page}) is not '
                    'supported. Only positive integers are supported.'
                )
            )
        try:
            raw_page_number = url_query_params.get('page_number')
            page_number = int(raw_page_number)
        except ValueError:
            return apitess.errors.error(
                400,
                data=url_query_params,
                message=(
                    f'Specified "page_number" value ({raw_page_number}) is '
                    'not supported. Only non-negative integers are supported.'
                )
            )
        if page_number < 0:
            return apitess.errors.error(
                400,
                data=url_query_params,
                message=(
                    f'Specified "page_number" value ({raw_page_number}) is '
                    'not supported. Only non-negative integers are supported.'
                )
            )
        page_options = tesserae.utils.search.PageOptions(
            sort_by=sort_by,
            sort_order=sort_order,
            per_page=per_page,
            page_number=page_number
        )

    search_id = results_status_found[0].id
    response = flask.Response(
        response=gzip.compress(flask.json.dumps({
            'data': params,
            'max_score': tesserae.utils.search.get_max_score(flask.g.db,
                                                             search_id),
            'total_count': tesserae.utils.search.get_results_count(flask.g.db,
                                                                   search_id),
            'parallels': tesserae.utils.search.get_results(
                flask.g.db, search_id, page_options)
        }).encode()),
        mimetype='application/json',
    )
    response.status_code = 200
    response.status = '200 OK'
    response.headers['Content-Encoding'] = 'gzip'

    results_status_found[0].update_last_queried()
    flask.g.db.update(results_status_found[0])
    return response
