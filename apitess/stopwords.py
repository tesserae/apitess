"""The family of /stopwords/ endpoints"""
import os

import flask
from flask_cors import cross_origin

import apitess.errors
import apitess.utils
import tesserae.db.entities
from tesserae.utils.stopwords import create_stoplist, get_stoplist_tokens

bp = flask.Blueprint('stopwords', __name__, url_prefix='/stopwords')


@bp.route('/')
@cross_origin()
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
            data={k: v
                  for k, v in flask.request.args.items()},
            message='"list_size" must be an integer')

    # language takes precedence over works
    language = flask.request.args.get('language', None)
    if language:
        stopword_indices = create_stoplist(flask.g.db, list_size, feature,
                                           language)
        if len(stopword_indices) == 0:
            return apitess.errors.error(
                400,
                data={k: v
                      for k, v in flask.request.args.items()},
                message='No stopwords found for feature "{}" in language "{}".'
                .format(feature, language))
        return flask.jsonify({
            'stopwords':
            get_stoplist_tokens(flask.g.db, stopword_indices, feature,
                                language)
        })

    works = flask.request.args.get('works', None)
    if works:
        oids, fails = apitess.utils.parse_works_arg(works)
        if fails:
            return apitess.errors.bad_object_ids(fails, flask.request.args)
        text_results = flask.g.db.find(tesserae.db.entities.Text.collection,
                                       _id=oids)
        if len(text_results) != len(oids):
            # figure out which works were not found in the database and report
            found = {str(r.id) for r in text_results}
            not_found = []
            for obj_id in oids:
                if obj_id not in found:
                    not_found.append(obj_id)
                return apitess.errors.error(
                    400,
                    data={k: v
                          for k, v in flask.request.args.items()},
                    message=('The following works could not be found '
                             f'in the database: {not_found}'))
        stopword_indices = create_stoplist(
            flask.g.db,
            list_size,
            feature,
            text_results[0].language,
            basis=[str(t.id) for t in text_results])
        return flask.jsonify({
            'stopwords':
            get_stoplist_tokens(flask.g.db, stopword_indices, feature,
                                language)
        })

    # if we get here, then we didn't get enough information
    return apitess.errors.error(
        400,
        data={k: v
              for k, v in flask.request.args.items()},
        message=(
            'Insufficient information was given to calculate a stopwords '
            'list (Perhaps you forgot to specify "language" or "works").'))


@bp.route('/lists/')
@cross_origin()
def query_stopwords_lists():
    """Report curated stopwords lists in database"""
    found = flask.g.db.find(tesserae.db.entities.StopwordsList.collection)
    return flask.jsonify({'list_names': [a.name for a in found]})


@bp.route('/lists/<name>/')
@cross_origin()
def get_stopwords_list(name):
    """Retrieve specified stopwords list"""
    found = flask.g.db.find(tesserae.db.entities.StopwordsList.collection,
                            name=name)
    if not found:
        return apitess.errors.error(
            404,
            name=name,
            message=(f'No list with the provided name ({name}) was found in '
                     'the database.'))
    return flask.jsonify({'name': name, 'stopwords': found[0].stopwords})


if os.environ.get('ADMIN_INSTANCE') == 'true':

    @bp.route('/lists/', methods=['POST'])
    def add_stopwords_list():
        error_response, data = apitess.errors.check_body(flask.request)
        if error_response:
            return error_response
        if 'name' not in data:
            return apitess.errors.error(
                400,
                data=data,
                message='"name" field missing from request data.')
        if not isinstance(data['name'], str):
            return apitess.errors.error(400,
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
            _ = flask.g.db.insert(
                tesserae.db.entities.StopwordsList(
                    name=data['name'], stopwords=data['stopwords']))
        except ValueError as e:
            if 'exists' in e.args[0]:
                return apitess.errors.error(
                    400,
                    data=data,
                    message=(f'The stopwords list name provided ({name}) '
                             'already exists in the database. If you meant to '
                             'update the stopwords list, try a DELETE at '
                             'https://tesserae.caset.buffalo.edu/texts/'
                             f'{name}/ first, then re-try this POST.'))
            return apitess.errors.error(500,
                                        data=data,
                                        message='Unknown server error')
        response = flask.jsonify({'stopwords': data['stopwords']})
        response.status_code = 201
        response.headers['Content-Location'] = os.path.join(
            flask.request.url_rule.rule, name, '')
        return response

    @bp.route('/lists/<name>/', methods=['DELETE'])
    def delete_stopwords_list(name):
        found = flask.g.db.find(tesserae.db.entities.StopwordsList.collection,
                                name=name)
        if not found:
            return apitess.errors.error(
                404,
                name=name,
                message='No stopwords list matches the specified name ({}).'.
                format(name))
        result = flask.g.db.delete(found[0])
        if result.deleted_count != 1:
            return apitess.errors.error(
                500,
                name=name,
                message='Server error in deleting: deleted {} documents'.
                format(result.deleted_count))
        response = flask.Response()
        response.status_code = 204
        return response
