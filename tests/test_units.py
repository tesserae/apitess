import json
import os

import flask
import werkzeug.datastructures

import tesserae.db.entities


def test_query_units_with_fields(populated_app, populated_client):
    response = populated_client.get('/texts/')
    assert response.status_code == 200
    data = response.get_json()
    text_id = data['texts'][0]['object_id']
    unit_type = 'line'
    with populated_app.test_request_context():
        endpoint = flask.url_for('units.query_units', text=text_id,
                unit_type=unit_type)
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'units' in data and isinstance(data['units'], list)
    assert len(data['units']) > 0
    for unit in data['units']:
        assert unit['text'] == text_id
        assert unit['unit_type'] == unit_type
