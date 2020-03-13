"""The family of /languages/ endpoints"""

import json
import os
import urllib.parse

from bson.objectid import ObjectId
from bson.errors import InvalidId
import flask
from flask_cors import cross_origin

import apitess.errors
from apitess.utils import fix_id
import tesserae.db.entities
import tesserae.utils


bp = flask.Blueprint('languages', __name__, url_prefix='/languages')


@bp.route('/')
@cross_origin()
def query_languages():
    """Consult database for available languages
    
    Returns
    -------
    languages : list of str
        The languages available to this database.
    """
    collection = tesserae.db.entities.Text.collection
    results = flask.g.db.connection[collection].distinct('language')
    return flask.jsonify(languages=list(results))

