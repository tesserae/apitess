import json
import os
import urllib.parse

import flask
import werkzeug.datastructures

import tesserae.db.entities


def test_query_units_empty(app, client):
    with app.test_request_context():
        endpoint = flask.url_for('units.query_units')
    response = client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'units' in data
    assert isinstance(data['units'], list)
    assert len(data['units']) == 0


def test_query_units_bad_object_id(app, client):
    with app.test_request_context():
        endpoint = flask.url_for('units.query_units', works='asdf')
    response = client.get(endpoint)
    assert response.status_code == 400


def test_query_units_with_fields(populated_app, populated_client):
    response = populated_client.get('/texts/')
    assert response.status_code == 200
    data = response.get_json()
    text_id = data['texts'][0]['object_id']
    unit_type = 'line'
    with populated_app.test_request_context():
        endpoint = flask.url_for('units.query_units', works=text_id,
                unit_type=unit_type)
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'units' in data and isinstance(data['units'], list)
    assert len(data['units']) > 0
    for unit in data['units']:
        assert unit['text'] == text_id
        assert unit['unit_type'] == unit_type


def test_query_units_with_multiple_texts(populated_app, populated_client):
    response = populated_client.get('/texts/')
    assert response.status_code == 200
    data = response.get_json()
    text_ids = [t['object_id'] for t in data['texts']]
    with populated_app.test_request_context():
        endpoint = flask.url_for('units.query_units',
                works=urllib.parse.quote(','.join(text_ids)),
                ignore='asdf')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'units' in data and isinstance(data['units'], list)
    assert len(data['units']) > 0
    for text in data['units']:
        assert text['text'] in text_ids

    with populated_app.test_request_context():
        endpoint = flask.url_for('units.query_units',
                works=','.join(text_ids),
                ignore='asdf')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'units' in data and isinstance(data['units'], list)
    assert len(data['units']) > 0
    for text in data['units']:
        assert text['text'] in text_ids


def test_query_units_with_multiple_units(populated_app, populated_client):
    with populated_app.test_request_context():
        endpoint = flask.url_for('units.query_units', unit_type='phrase')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    unit_ids = [u['object_id'] for u in data['units']]
    with populated_app.test_request_context():
        endpoint = flask.url_for('units.query_units',
                unit_ids=urllib.parse.quote(','.join(unit_ids)),
                ignore='asdf')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'units' in data and isinstance(data['units'], list)
    assert len(data['units']) == len(unit_ids)
    for unit in data['units']:
        assert unit['object_id'] in unit_ids

    with populated_app.test_request_context():
        endpoint = flask.url_for('units.query_units',
                unit_ids=','.join(unit_ids),
                ignore='asdf')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'units' in data and isinstance(data['units'], list)
    assert len(data['units']) == len(unit_ids)
    for unit in data['units']:
        assert unit['object_id'] in unit_ids
