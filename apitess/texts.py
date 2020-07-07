"""The family of /texts/ endpoints"""
import os
import urllib.parse
import uuid

from bson.objectid import ObjectId
import flask
from flask_cors import cross_origin

import apitess.errors
from apitess.utils import fix_id
import tesserae.db.entities
import tesserae.utils


bp = flask.Blueprint('texts', __name__, url_prefix='/texts')


@bp.route('/')
@cross_origin()
def query_texts():
    """Consult database for text metadata"""
    alloweds = {'author', 'is_prose', 'language', 'title'}
    filters = {}
    for allowed in alloweds:
        grabbed = flask.request.args.get(allowed, None)
        if grabbed:
            filters[allowed] = grabbed
    before_val = flask.request.args.get('before', None)
    after_val = flask.request.args.get('after', None)
    try:
        if before_val is not None:
            before_val = int(before_val)
        if after_val is not None:
            after_val = int(after_val)
    except ValueError:
        return apitess.errors.error(
            400,
            message='If used, "before" and "after" must have integer values.')

    if before_val is not None and after_val is not None:
        results = flask.g.db.find(
            tesserae.db.entities.Text.collection,
            year_not=(before_val, after_val),
            **filters)
    elif before_val is not None and after_val is None:
        results = flask.g.db.find(
            tesserae.db.entities.Text.collection,
            # Assuming that lower limit pre-dates all texts in database
            year=(-999999999999, before_val),
            **filters)
    elif before_val is None and after_val is not None:
        results = flask.g.db.find(
            tesserae.db.entities.Text.collection,
            # Assuming that upper limit post-dates all texts in database
            year=(after_val, 999999999999),
            **filters)
    else:
        results = flask.g.db.find(
            tesserae.db.entities.Text.collection,
            **filters)
    return flask.jsonify(texts=[fix_id(r.json_encode()) for r in results])


@bp.route('/<object_id>/')
@cross_origin()
def get_text(object_id):
    """Retrieve specific text's metadata"""
    results, failures = apitess.utils.make_object_ids([object_id])
    if failures:
        return apitess.errors.bad_object_id(object_id)
    object_id_obj = results[0]
    found = flask.g.db.find(
        tesserae.db.entities.Text.collection,
        _id=object_id_obj)
    if not found:
        return apitess.errors.text_not_found_object_id(object_id)
    result = fix_id(found[0].json_encode())
    return flask.jsonify(result)


if os.environ.get('ADMIN_INSTANCE') == 'true':
    FILE_UPLOAD_DIR = os.path.join(os.path.expanduser('~'), 'tess_data',
                                   'tessfiles')

    @bp.route('/', methods=['POST'])
    def add_text():
        os.makedirs(os.path.abspath(FILE_UPLOAD_DIR), exist_ok=True)
        received = flask.request.get_json()
        requireds = {'metadata', 'file_contents'}
        error_response = apitess.errors.check_requireds(received, requireds)
        if error_response:
            return error_response

        text = received['metadata']
        requireds = {'author', 'is_prose', 'language',
                     'title', 'year'}
        error_response = apitess.errors.check_requireds(text, requireds)
        if error_response:
            return error_response

        prohibiteds = {'_id', 'id', 'object_id'}
        error_response = apitess.errors.check_prohibited(text, prohibiteds)
        if error_response:
            return error_response

        # save uploaded file to local filesystem
        file_location = os.path.join(FILE_UPLOAD_DIR,
                                     str(uuid.uuid4()) + '.tess')
        with open(file_location, 'w', encoding='utf-8') as ofh:
            ofh.write(received['file_contents'])

        # remove ingestion status information, if provided
        if 'ingestion_status' in text:
            del text['ingestion_status']
        if 'ingestion_msg' in text:
            del text['ingestion_msg']

        text_to_add = tesserae.db.entities.Text(**text)
        try:
            # add text to database
            insert_id = tesserae.utils.ingest.submit_ingest(
                flask.g.ingest_queue, flask.g.db,
                text_to_add,
                file_location)
        except Exception as e:
            return apitess.errors.error(
                500,
                data=received,
                message='Could not add to database: {}'.format(e))

        object_id = str(insert_id)
        created = tesserae.utils.fix_id(text.decode_json())
        created['object_id'] = object_id
        percent_encoded_object_id = urllib.parse.quote(object_id)

        response = flask.Response()
        response.status_code = 201
        response.status = '201 Created'
        response.headers['Content-Location'] = os.path.join(
            flask.request.base_url, percent_encoded_object_id, '')
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.set_data(flask.json.dumps(created).encode('utf-8'))
        return response

    @bp.route('/<object_id>/', methods=['PATCH'])
    def update_text(object_id):
        error_message = apitess.errors.check_object_id(object_id)
        if error_message:
            return error_message

        received = flask.request.get_json()
        found = flask.g.db.find(
            tesserae.db.entities.Text.collection,
            _id=ObjectId(object_id))
        if not found:
            return apitess.errors.error(
                404,
                object_id=object_id,
                data=received,
                message=(f'No text with the provided identifier ({object_id}) '
                         'was found in the database.')
            )

        prohibited = {'_id', 'id', 'object_id'}
        error_response = apitess.errors.check_prohibited(received, prohibited)
        if error_response:
            return error_response

        found = found[0]
        found.__dict__.update(received)
        updated = flask.g.db.update(found)
        if updated.matched_count != 1:
            return apitess.errors.error(
                500,
                object_id=object_id,
                data=received,
                message=('Unexpected number of updates: '
                         f'{updated.matched_count}'))
        return get_text(object_id)

    @bp.route('/<object_id>/', methods=['DELETE'])
    def delete_text(object_id):
        error_message = apitess.errors.check_object_id(object_id)
        if error_message:
            return error_message
        found = flask.g.db.find(
            tesserae.db.entities.Text.collection,
            _id=ObjectId(object_id))
        if not found:
            return apitess.errors.error(
                404,
                object_id=object_id,
                message=(f'No text with the provided identifier ({object_id}) '
                         'was found in the database.')
            )
        # TODO check for proper deletion?
        flask.g.db.delete(found).deleted_count
        response = flask.Response()
        response.status_code = 204
        response.status = '204 No Content'
        return response
