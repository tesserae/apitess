import json
import os

import flask
import werkzeug.datastructures

import tesserae.db.entities


def test_query_tokens_with_fields(populated_app, populated_client):
    response = populated_client.get('/texts/')
    assert response.status_code == 200
    data = response.get_json()
    text_id = data['texts'][0]['object_id']
    with populated_app.test_request_context():
        endpoint = flask.url_for('tokens.query_tokens', text=text_id)
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'tokens' in data and isinstance(data['tokens'], list)
    assert len(data['tokens']) > 0
    for token in data['tokens']:
        assert token['text'] == text_id
