"""A place for error message code"""
from bson.objectid import ObjectId
import flask
from werkzeug.exceptions import BadRequest


def error(status_code, **kwargs):
    response = flask.jsonify(**kwargs)
    response.status_code = status_code
    return response


def bad_object_id(object_id):
    return error(
        400,
        object_id=object_id,
        message='Provided identifier ({}) is malformed.'.format(object_id))


def check_object_id(object_id):
    """Checks whether the string could be a well-formed ObjectId

    If the string could not be made into an ObjectId, an error message will be
    returned by this function.

    If the string coult be made into an ObjectId, None is returned by this
    function.
    """
    if not ObjectId.is_valid(object_id):
        return bad_object_id(object_id)
    return None


def bad_object_ids(object_ids, args):
    return error(400,
                 data={k: v
                       for k, v in args.items()},
                 message=('The following identifiers were malformed: '
                          '{}'.format(object_ids)))


def text_not_found_object_id(object_id):
    return error(
        404,
        object_id=object_id,
        message=(f'No text with the provided identifier ({object_id}) was '
                 'found in the database.'))


def check_requireds(received, requireds):
    """Checks whether required keys are found in received dictionary

    If any required keys are missing, they will be collected into an error
    message, and this error message will be returned by this function as an
    error response.

    If all required keys are found, None is returned by this function.
    """
    missing = []
    for req in requireds:
        if req not in received:
            missing.append(req)
    if missing:
        return error(
            400,
            data=received,
            message=('The request data payload is missing the following '
                     'required key(s): {}'.format(', '.join(missing))))
    return None


def check_prohibited(received, prohibited):
    """Checks whether prohibited keys are found in received dictionary

    If any prohibited keys are present, they will be collected into an error
    message, and this error message will be returned by this function as an
    error response.

    If no prohibited keys are found, None is returned by this function.
    """
    found = []
    for key in prohibited:
        if key in received:
            found.append(key)
    if found:
        return error(
            400,
            data=received,
            message=('The request data payload contains the following '
                     'prohibited key(s): {}'.format(', '.join(found))))
    return None


def check_body(request):
    """Checks whether the body of the request contains parsable JSON

    Returns
    -------
    error_response
        If there were problems parsing the body of the request as JSON, this
        will be set to an error response; otherwise, this will be set to None
    received
        If there were no problems parsing the body of the request as JSON, this
        will be set to the JSON object; otherwise, this will be set to None
    """
    if not flask.request.data:
        return error(
            400,
            data='',
            message=('No search parameters were sent with the request')), None
    try:
        received = flask.request.get_json()
    except BadRequest:
        return error(
            400,
            data=flask.request.data.decode('utf-8'),
            message=('Unable to parse search parameters; perhaps the JSON '
                     'data is malformed')), None
    if received is None:
        return error(400,
                     data=flask.request.data.decode('utf-8'),
                     message=('Unable to parse search parameters; perhaps the '
                              'Content-Type header was not set correctly to '
                              '"application/json; charset=utf-8"')), None
    return None, received
