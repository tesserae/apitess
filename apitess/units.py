"""The family of /units/ endpoints"""
import json

from bson.objectid import ObjectId
import flask

from apitess.utils import fix_id
import tesserae


bp = flask.Blueprint('units', __name__, url_prefix='/units')


@bp.route('/')
def query_units():
    """Consult database for text metadata"""
    alloweds = {'unit_type'}
    filters = {}
    for allowed in alloweds:
        grabbed = flask.request.args.get(allowed, None)
        if grabbed:
            filters[allowed] = grabbed
    special_alloweds = {'text'}
    for allowed in special_alloweds:
        grabbed = flask.request.args.get(allowed, None)
        if grabbed:
            filters[allowed] = ObjectId(grabbed)
    results = [fix_id(r.json_encode()) for r in flask.g.db.find(
        tesserae.db.entities.Unit.collection,
        **filters)]
    for unit in results:
        text_obj_id = unit['text']
        unit['text'] = str(text_obj_id)
    return flask.jsonify(units=results)
