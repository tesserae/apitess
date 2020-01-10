"""The family of /tokens/ endpoints"""
import json

from bson.objectid import ObjectId
import flask

from apitess.utils import fix_id
import tesserae


bp = flask.Blueprint('tokens', __name__, url_prefix='/tokens')


@bp.route('/')
def query_tokens():
    """Consult database for text metadata"""
    special_alloweds = {'text'}
    filters = {}
    for allowed in special_alloweds:
        grabbed = flask.request.args.get(allowed, None)
        if grabbed:
            filters[allowed] = ObjectId(grabbed)
    results = [fix_id(r.json_encode()) for r in flask.g.db.find(
        tesserae.db.entities.Token.collection,
        **filters)]
    for token in results:
        text_obj_id = token['text']
        token['text'] = str(text_obj_id)
        token_features = token['features']
        for k, v in token_features:
            if isinstance(v, list):
                token_features[k] = [str(obj_id) for obj_id in v]
            else:
                token_features[k] = str(v)
    return flask.jsonify(tokens=results)
