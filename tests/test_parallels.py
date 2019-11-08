import gzip
import json
import time

import flask
import pytest
import werkzeug.datastructures

import tesserae.db.entities


def test_search(populated_app, populated_client):
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        found_texts = flask.g.db.find(tesserae.db.entities.Text.collection)
        submit_endpoint = flask.url_for('parallels.submit_search')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    search_query = {
        'source': {'object_id': str(found_texts[0].id), 'units': 'line'},
        'target': {'object_id': str(found_texts[1].id), 'units': 'line'},
        'method': {'name': 'original',
            'feature': 'lemmata',
            'stopwords': ['et', 'qui', 'quis'],
            'freq_basis': 'corpus',
            'max_distance': 6,
            'distance_basis': 'frequency'}}
    response = populated_client.post(submit_endpoint,
            data=json.dumps(search_query), headers=headers)
    assert response.status_code == 201
    assert 'Location' in response.headers
    results_id = response.headers['Location'].split('/')[-2]
    # TODO wait for appropriate time until search is complete
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                results_id=results_id)
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
