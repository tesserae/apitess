"""The family of /parallels/ endpoints"""
import gzip
import os
import queue
import uuid

from bson.objectid import ObjectId
import flask

import tesserae.db.entities
from tesserae.matchers.sparse_encoding import SparseMatrixSearch
from tesserae.utils.retrieve import get_results
from tesserae.utils.search import check_cache
import apitess.errors

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


@bp.route('/', methods=('POST',))
def submit_search():
    """Run a Tesserae search"""
    received = flask.request.get_json()
    requireds = {'source', 'target', 'method'}
    missing = []
    for req in requireds:
        if req not in received:
            missing.append(req)
    if missing:
        return apitess.errors.error(
            400,
            data=received,
            message='The request data payload is missing the following required key(s): {}'.format(', '.join(missing)))

    source = received['source']
    target = received['target']

    errors = _validate_units(source, 'source')
    errors.extend(_validate_units(target, 'target'))
    if errors:
        return apitess.errors.error(
            400,
            data=received,
            message='The following errors were found in source and target unit specifications:\n{}'.format('\n\t'.join(errors)))

    source_object_id = source['object_id']
    target_object_id = target['object_id']
    results = flask.g.db.find(tesserae.db.entities.Text.collection,
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
            message='Unable to find the following object_id(s) among the texts in the database:\n\t{}'.format('\n\t'.join(errors)))
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
            message='The specified method is missing the following required key(s): {}'.format(', '.join(missing)))

    results_id = check_cache(flask.g.db, source, target, method)
    if results_id:
        response = flask.Response()
        response.status_code = 303
        response.status = '303 See Other'
        # we want the final '/' on the URL
        response.headers['Location'] = os.path.join(bp.url_prefix, results_id, '')
        return response

    response = flask.Response()
    response.status_code = 201
    response.status = '201 Created'
    results_id = uuid.uuid4().hex
    # we want the final '/' on the URL
    response.headers['Location'] = os.path.join(bp.url_prefix, results_id, '')

    try:
        flask.g.searcher.queue_search(results_id, method['name'], {
            'texts': [source_text, target_text],
            'unit_type': received['source']['units'],
            'feature': method['feature'],
            'stopwords': method['stopwords'],
            'frequency_basis': method['freq_basis'],
            'max_distance': method['max_distance'],
            'distance_metric': method['distance_basis'],
            'min_score': 0
        })
    except queue.Full:
        return apitess.error.error(
            500,
            data=received,
            message=('The search request could not be added to the queue. '
                'Please try again in a few minutes'))
    return response


@bp.route('/status/<results_id>/')
def retrieve_status(results_id):
    results_status_found = flask.g.db.find(
        tesserae.db.entities.Search.collection,
        results_id=results_id
    )
    if not results_status_found:
        response = flask.Response('Could not find results_id')
        response.status_code = 404
        return response
    status = results_status_found[0]
    return flask.jsonify(results_id=status.results_id, status=status.status,
            message=status.msg)


@bp.route('/<results_id>/')
def retrieve_results(results_id):
    # get search results
    results_status_found = flask.g.db.find(
        tesserae.db.entities.Search.collection,
        results_id=results_id
    )
    if not results_status_found:
        response = flask.Response('Could not find results_id')
        response.status_code = 404
        return response
    if results_status_found[0].status != tesserae.db.entities.Search.DONE:
        response = flask.Response(
                'Unable to retrieve results; check /status/ endpoint.')
        reponse.status_code = 404
        return response

    params = results_status_found[0].parameters

    matches = [m for m in get_results(flask.g.db, results_id)]
    response = flask.Response(
        response=gzip.compress(flask.json.dumps({
            'data': params,
            'parallels': matches
        }).encode()),
        mimetype='application/json',
    )
    response.status_code = 200
    response.status = '200 OK'
    response.headers['Content-Encoding'] = 'gzip'
    return response
