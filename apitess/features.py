"""The family of /features/ endpoints"""
import json

from bson.objectid import ObjectId
import flask

from apitess.utils import fix_id
import tesserae


bp = flask.Blueprint('features', __name__, url_prefix='/features')


@bp.route('/')
def query_features():
    """Consult database for text metadata"""
    alloweds = {'language', 'feature', 'token'}
    filters = {}
    for allowed in alloweds:
        grabbed = flask.request.args.get(allowed, None)
        if grabbed:
            filters[allowed] = grabbed
    results = [fix_id(r.json_encode()) for r in flask.g.db.find(
        tesserae.db.entities.Feature.collection,
        **filters)]
    for feature in results:
        feature_freqs = feature['frequencies']
        tmp = {}
        for k, v in feature_freqs.items():
            tmp[str(k)] = v
        feature['frequencies'] = tmp
    return flask.jsonify(features=results)

