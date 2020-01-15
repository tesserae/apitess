"""A place for error message code"""
import urllib.parse

import flask


def error(status_code, **kwargs):
    response = flask.jsonify(**kwargs)
    response.status_code = status_code
    return response


def bad_object_id(object_id):
    return error(
        400,
        object_id=object_id,
        message='Provided identifier ({}) is malformed.'.format(object_id))


def bad_object_ids(object_ids, args):
    return error(
        400,
        data={k: v for k, v in args.items()},
        message='The following identifiers were malformed: {}'.format(object_ids))


def text_not_found_object_id(object_id):
    return apitess.errors.error(
        404,
        object_id=object_id,
        message='No text with the provided identifier ({}) was found in the database.'.format(object_id))
