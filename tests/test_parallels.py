import gzip
import json
import time

import flask
import pytest
import werkzeug.datastructures

import tesserae.db.entities


def test_search(populated_app, populated_client):
    # request a search
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

    # wait until search completes
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        status_endpoint = flask.url_for('parallels.retrieve_status',
                results_id=results_id)
    response = populated_client.get(status_endpoint)
    while response.status_code == 404:
        response = populated_client.get(status_endpoint)
        time.sleep(0.1)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    assert status != tesserae.db.entities.Search.FAILED, data['message']
    while status != tesserae.db.entities.Search.DONE:
        response = populated_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
        assert status != tesserae.db.entities.Search.FAILED, data['message']
        time.sleep(0.1)

    # make sure we can retrieve results
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                results_id=results_id)
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert len(data['parallels']) > 0

    # make sure search results were cached
    response = populated_client.post(submit_endpoint,
            data=json.dumps(search_query), headers=headers)
    assert response.status_code == 303
    assert 'Location' in response.headers
    assert results_id == response.headers['Location'].split('/')[-2]


def test_bad_feature_search(populated_app, populated_client):
    bad_feature = 'DEADBEEF'

    # request a bad search
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
            # !!! bad feature
            'feature': bad_feature,
            'stopwords': ['et', 'qui', 'quis'],
            'freq_basis': 'corpus',
            'max_distance': 6,
            'distance_basis': 'frequency'}}
    response = populated_client.post(submit_endpoint,
            data=json.dumps(search_query), headers=headers)
    assert response.status_code == 201
    assert 'Location' in response.headers
    results_id = response.headers['Location'].split('/')[-2]

    # make sure bad feature was caught
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        status_endpoint = flask.url_for('parallels.retrieve_status',
                results_id=results_id)
    response = populated_client.get(status_endpoint)
    while response.status_code == 404:
        response = populated_client.get(status_endpoint)
        time.sleep(0.1)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    while status != tesserae.db.entities.Search.FAILED:
        response = populated_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
        time.sleep(0.1)
    assert status == tesserae.db.entities.Search.FAILED
    assert 'message' in data
    assert f'"{bad_feature}"' in data['message']


def test_non_existent_results(populated_app, populated_client):
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                results_id='does-not-exist')
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 404


def test_search_bad_request(populated_app, populated_client):
    # request a search
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        found_texts = flask.g.db.find(tesserae.db.entities.Text.collection)
        submit_endpoint = flask.url_for('parallels.submit_search')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    search_query = {
        'source': {'object_id': str(found_texts[0].id), 'units': 'line'},
        'target': {'object_id': str(found_texts[1].id), 'units': 'line'},
    }
    response = populated_client.post(submit_endpoint,
            data=json.dumps(search_query), headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    for k1, v1 in search_query.items():
        assert k1 in data['data']
        rv1 = data['data'][k1]
        for k2, v2 in v1.items():
            assert k2 in rv1
            assert rv1[k2] == v2
    assert 'method' in data['message'].split(': ')[-1].split(',')
