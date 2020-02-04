"""The family of /languages/ endpoints"""

import json
import os
import urllib.parse

from bson.objectid import ObjectId
from bson.errors import InvalidId
import flask

import apitess.errors
from apitess.utils import fix_id
import tesserae.db.entities
import tesserae.utils


bp = flask.Blueprint('languages', __name__, url_prefix='/languages')


@bp.route('/')
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


@bp.route('/<language>/')
def get_language_stats(language):
    """Retrive statistics and information about a language in the database.
    
    Returns
    -------
    stats : dict
        Various information about the texts and features of the language
        in the database.
    """
    language = language.lower()
    stats = {
        'language': language
    }

    collection = tesserae.db.entities.Text.collection
    stats['texts'] = flask.g.db.find(collection, language=language)

    if len(stats['texts']) > 0:
        collection = tesserae.db.entities.Feature.collection
        result = flask.g.db.aggregate(collection, [
            {'$match': {'language': language}},
            {'$sort': {'token': 1}},
            {'$group': {
                '_id': '$feature',
                'tokens': {'$push': '$token'}
            }},
            {'$project': {
                '_id': True,
                'tokens': True,
                'count': {'$size': '$tokens'}
            }}
        ])
        stats['features'] = {
            f['_id']: {'count': f['count'], 'tokens': f['tokens']}
            for f in result}
        return flask.jsonify(stats=stats)
    else:
        return apitess.errors.error(
            404,
            language=language,
            message=f'Corpus contains no {language} texts.'
        )