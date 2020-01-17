import json
import os

import flask
import werkzeug.datastructures

import tesserae.db.entities


def test_query_features_empty(app, client):
    with app.test_request_context():
        endpoint = flask.url_for('features.query_features')
    response = client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'features' in data
    assert isinstance(data['features'], list)
    assert len(data['features']) == 0


def test_query_features_with_fields(populated_app, populated_client):
    feature = 'lemmata'
    with populated_app.test_request_context():
        endpoint = flask.url_for('features.query_features', feature=feature,
                ridiculous='qwer')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'features' in data and isinstance(data['features'], list)
    assert len(data['features']) > 0
    for unit in data['features']:
        assert 'object_id' not in unit
        assert 'feature' in unit
        assert unit['feature'] == feature
        assert 'language' in unit
        assert 'token' in unit
        assert 'index' in unit
        assert 'frequencies' in unit
