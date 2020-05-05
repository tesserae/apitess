"""The family of /units/ endpoints"""
import json

from bson.objectid import ObjectId
import flask
from flask_cors import cross_origin

import apitess.utils
import tesserae


bp = flask.Blueprint('units', __name__, url_prefix='/units')


@bp.route('/')
@cross_origin()
def query_units():
    """Consult database for unit information"""
    if len(flask.request.args) == 0:
        # default response
        return flask.jsonify(units=[])
    alloweds = {'unit_type'}
    filters = {}
    for allowed in alloweds:
        grabbed = flask.request.args.get(allowed, None)
        if grabbed:
            filters[allowed] = grabbed
    works = flask.request.args.get('works', None)
    if works:
        oids, fails = apitess.utils.parse_works_arg(works)
        if fails:
            return apitess.errors.bad_object_ids(fails, flask.request.args)
        filters['text'] = oids
    unit_ids = flask.request.args.get('unit_ids', None)
    if unit_ids:
        oids, fails = apitess.utils.parse_works_arg(unit_ids)
        if fails:
            return apitess.errors.bad_object_ids(fails, flask.request.args)
        filters['_id'] = oids
    results = [{
            "object_id": str(r.id),
            "index": r.index,
            "snippet": r.snippet,
            "tags": r.tags,
            "text": str(r.text),
            "tokens": r.tokens,
            "unit_type": r.unit_type,
        } for r in flask.g.db.find(
        tesserae.db.entities.Unit.collection,
        **filters)]
    return flask.jsonify(units=results)
