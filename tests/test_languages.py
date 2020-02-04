import json
import os

import flask


def test_query_languages(populated_client):
    response = populated_client.get('/languages/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'languages' in data
    assert isinstance(data['languages'], list)
    assert 'greek' in data['languages']
    assert 'latin' in data['languages']


def test_get_language_stats(populated_client):
    pass