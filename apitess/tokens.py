"""The family of /tokens/ endpoints"""
import json
import urllib.parse

from bson.objectid import ObjectId
import flask

import apitess.errors
from apitess.utils import fix_id
import tesserae


bp = flask.Blueprint('tokens', __name__, url_prefix='/tokens')


@bp.route('/')
def query_tokens():
    """Consult database for token information"""
    if len(flask.request.args) == 0:
        # default response
        return flask.jsonify(tokens=[])
    works = flask.request.args.get('works', None)
    if works:
        oids, fails = apitess.utils.parse_works_arg(works)
        if fails:
            return apitess.errors.bad_object_ids(fails, flask.request.args)
        token_results = flask.g.db.find(
            tesserae.db.entities.Token.collection,
            text=oids)
        return flask.jsonify(tokens=[
            {'text': str(t.text), 'index': t.index, 'display': t.display}
            for t in token_results])

    # if we get here, we didn't get enough information
    return apitess.errors.error(
            400,
            data={k: v for k, v in flask.request.args.items()},
            message='Unknown keyword(s) (Perhaps you meant "works").')
