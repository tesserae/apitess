"""The family of /stopwords/ endpoints"""
import json
import os

from bson.objectid import ObjectId
import flask

import apitess.errors
import tesserae.db.entities
from tesserae.matchers.sparse_encoding import SparseMatrixSearch

bp = flask.Blueprint('stopwords', __name__, url_prefix='/stopwords')


def indices_to_tokens(connection, stopword_indices, language, feature):
    results = connection.find(
        tesserae.db.entities.Feature.collection,
        index=[int(i) for i in stopword_indices],
        language=language,
        feature=feature)
    results = {f.index: f.token for f in results}
    return [results[i] for i in stopword_indices]


@bp.route('/')
def query_stopwords():
    """Build a stopwords list"""
    if len(flask.request.args) == 0:
        # default response when no arguments are given
        return flask.jsonify({'stopwords': []})

    feature = flask.request.args.get('feature', 'lemmata')
    list_size = flask.request.args.get('list_size', 10)
    try:
        list_size = int(list_size)
    except ValueError:
        return apitess.errors.error(
                400,
                data={k: v for k, v in flask.request.args.items()},
                message='"list_size" must be an integer')

    searcher = SparseMatrixSearch(flask.g.db)
    # language takes precedence over works
    language = flask.request.args.get('language', None)
    if language:
        stopword_indices = searcher.create_stoplist(list_size, feature,
                language)
        if len(stopword_indices) == 0:
            return apitess.errors.error(
                    400,
                    data={k: v for k, v in flask.request.args.items()},
                    message='No stopwords found for feature "{}" in language "{}".'.format(feature, language))
        return flask.jsonify(
                {'stopwords': indices_to_tokens(flask.g.db, stopword_indices,
                    language, feature)})

    works = flask.request.args.get('works', None)
    if works:
        if ',' in works:
            works = works.split(',')
        else:
            works = [works]
        text_results = flask.g.db.find(
            tesserae.db.entities.Text.collection,
            _id=[ObjectId(w) for w in works])
        if len(text_results) != len(works):
            # figure out which works were not found in the database and report
            found = {str(r.id) for r in text_results}
            not_found = []
            for work in works:
                if work not in found:
                    not_found.append(work)
                return apitess.errors.error(
                        400,
                        data={k: v for k, v in flask.request.args.items()},
                        message='The following works could not be found in the database: {}'.format(not_found))
        stopword_indices = searcher.create_stoplist(list_size, feature,
                text_results[0].language, basis=[str(t.id) for t in text_results])
        return flask.jsonify(
                {'stopwords': indices_to_tokens(flask.g.db, stopword_indices,
                    language, feature)})

    # if we get here, then we didn't get enough information
    return apitess.errors.error(
            400,
            data={k: v for k, v in flask.request.args.items()},
            message='Insufficient information was given to calculate a stopwords list (Perhaps you forgot to specify "language" or "works").')


@bp.route('/lists/')
def query_stopwords_lists():
    """Report curated stopwords lists in database"""
    found = flask.g.db.find(
        tesserae.db.entities.StopwordsList.collection
    )
    return flask.jsonify({'list_names': [a.name for a in found]})


@bp.route('/lists/<name>/')
def get_stopwords_list(name):
    """Retrieve specified stopwords list"""
    found = flask.g.db.find(
        tesserae.db.entities.StopwordsList.collection,
        name=name
    )
    if not found:
        return apitess.errors.error(
            404,
            name=name,
            message='No list with the provided name ({}) was found in the database.'.format(name))
    return flask.jsonify({'name': name, 'stopwords': found[0].stopwords})


if os.environ.get('ADMIN_INSTANCE') == 'true':
    @bp.route('/lists/', methods=['POST'])
    def add_stopwords_list():
        data = flask.request.get_json()
        if 'name' not in data:
            return apitess.errors.error(
                400,
                data=data,
                message='"name" field missing from request data.')
        if not isinstance(data['name'], str):
            return apitess.errors.error(
                400,
                data=data,
                message='"name" must be a string.')
        if 'stopwords' not in data:
            return apitess.errors.error(
                400,
                data=data,
                message='"stopwords" field missing from request data.')
        if not isinstance(data['stopwords'], list):
            return apitess.errors.error(
                400,
                data=data,
                message='"stopwords" must be a list of strings.')
        for stopword in data['stopwords']:
            if not isinstance(stopword, str):
                return apitess.errors.error(
                    400,
                    data=data,
                    message='"stopwords" must be a list of strings.')

        name = data['name']

        try:
            found = flask.g.db.insert(
                tesserae.db.entities.StopwordsList(
                    name=data['name'],
                    stopwords=data['stopwords']
                )
            )
        except ValueError as e:
            if 'exists' in e.args[0]:
                return apitess.errors.error(
                    400,
                    data=data,
                    message='The stopwords list name provided ({0}) already exists in the database. If you meant to update the stopwords list, try a DELETE at https://tesserae.caset.buffalo.edu/texts/{0}/ first, then re-try this POST.'.format(name))
            return apitess.errors.error(
                500,
                data=data,
                message='Unknown server error'
            )
        response = flask.jsonify({'stopwords': data['stopwords']})
        response.status_code = 201
        response.headers['Content-Location'] = os.path.join(
            flask.request.url_rule.rule, name, '')
        return response


    @bp.route('/lists/<name>/', methods=['DELETE'])
    def delete_stopwords_list(name):
        found = flask.g.db.find(
            tesserae.db.entities.StopwordsList.collection,
            name=name
        )
        if not found:
            return apitess.errors.error(
                404,
                name=name,
                message='No stopwords list matches the specified name ({}).'.format(name))
        result = flask.g.db.delete(found[0])
        if result.deleted_count != 1:
            return apitess.errors.error(
                500,
                name=name,
                message='Server error in deleting: deleted {} documents'.format(result.deleted_count)
            )
        response = flask.Response()
        response.status_code = 204
        return response
