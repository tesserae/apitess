import json
import os
import urllib.parse

import flask
import werkzeug.datastructures

import tesserae.db.entities


def test_query_tokens_empty(app, client):
    with app.test_request_context():
        endpoint = flask.url_for('tokens.query_tokens')
    response = client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'tokens' in data
    assert isinstance(data['tokens'], list)
    assert len(data['tokens']) == 0


def test_query_tokens_bad_keyword(app, client):
    with app.test_request_context():
        endpoint = flask.url_for('tokens.query_tokens', texts='asdf')
    response = client.get(endpoint)
    assert response.status_code == 400


def test_query_tokens_bad_object_id(app, client):
    with app.test_request_context():
        endpoint = flask.url_for('tokens.query_tokens', works='asdf')
    response = client.get(endpoint)
    assert response.status_code == 400


def test_query_tokens_with_one_text(populated_app, populated_client):
    response = populated_client.get('/texts/')
    assert response.status_code == 200
    data = response.get_json()
    text_ids = [t['object_id'] for t in data['texts']]
    with populated_app.test_request_context():
        endpoint = flask.url_for('tokens.query_tokens', works=text_ids[0],
                ignore='asdf')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'tokens' in data and isinstance(data['tokens'], list)
    assert len(data['tokens']) > 0
    for token in data['tokens']:
        assert token['text'] == text_ids[0]

def test_query_tokens_with_multiple_texts(populated_app, populated_client):
    response = populated_client.get('/texts/')
    assert response.status_code == 200
    data = response.get_json()
    text_ids = [t['object_id'] for t in data['texts']]
    with populated_app.test_request_context():
        endpoint = flask.url_for('tokens.query_tokens',
                works=urllib.parse.quote(','.join(text_ids)),
                ignore='asdf')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'tokens' in data and isinstance(data['tokens'], list)
    assert len(data['tokens']) > 0
    for token in data['tokens']:
        assert token['text'] in text_ids

    with populated_app.test_request_context():
        endpoint = flask.url_for('tokens.query_tokens',
                works=','.join(text_ids),
                ignore='asdf')
    response = populated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert 'tokens' in data and isinstance(data['tokens'], list)
    assert len(data['tokens']) > 0
    for token in data['tokens']:
        assert token['text'] in text_ids
