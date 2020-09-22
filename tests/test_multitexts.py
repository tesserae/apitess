import gzip
import json
import time

import flask
import werkzeug.datastructures

import tesserae.db.entities


def test_multitexts(multitext_app, multitext_client):
    # request a search
    print('Submitting search')
    with multitext_app.test_request_context():
        multitext_app.preprocess_request()
        found_texts = flask.g.db.find(tesserae.db.entities.Text.collection)
        submit_endpoint = flask.url_for('parallels.submit_search')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    search_query = {
        'source': {
            'object_id': str(found_texts[0].id),
            'units': 'line'
        },
        'target': {
            'object_id': str(found_texts[1].id),
            'units': 'line'
        },
        'method': {
            'name': 'original',
            'feature': 'lemmata',
            'stopwords': ['et', 'qui', 'quis'],
            'score_basis': 'lemmata',
            'freq_basis': 'corpus',
            'max_distance': 6,
            'distance_basis': 'frequency'
        }
    }
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 201
    assert 'Location' in response.headers
    search_results_id = response.headers['Location'].split('/')[-2]

    # wait until search completes
    print('Waiting for search to complete')
    with multitext_app.test_request_context():
        multitext_app.preprocess_request()
        status_endpoint = flask.url_for('parallels.retrieve_status',
                                        results_id=search_results_id)
    response = multitext_client.get(status_endpoint)
    while response.status_code == 404:
        time.sleep(0.1)
        response = multitext_client.get(status_endpoint)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    assert status != tesserae.db.entities.Search.FAILED, data['message']
    while status != tesserae.db.entities.Search.DONE:
        time.sleep(0.1)
        response = multitext_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
        assert status != tesserae.db.entities.Search.FAILED, data['message']

    # make sure we can retrieve results
    print('Retrieving search results')
    with multitext_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id)
    response = multitext_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert len(data['parallels']) > 0

    # make sure search results were cached
    print('Verifying that search results were cached')
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 303
    assert 'Location' in response.headers
    assert search_results_id == response.headers['Location'].split('/')[-2]

    #
    # Set up submission for multitext search
    #
    with multitext_app.test_request_context():
        multitext_app.preprocess_request()
        found_texts = flask.g.db.find(tesserae.db.entities.Text.collection)
        submit_endpoint = flask.url_for('multitexts.submit_multitext')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'

    # perform bad multitext search submissions
    print('Submitting no texts')
    search_query = {
        'parallels_uuid': search_results_id,
        'text_ids': [],
        'unit_type': 'line'
    }
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 400
    print('Submitting bad text id')
    bad_id = 'bad-id'
    search_query = {
        'parallels_uuid': search_results_id,
        'text_ids': [bad_id],
        'unit_type': 'line'
    }
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert bad_id in data['message']
    print('Submitting bad unit_type')
    bad_unit = 'bad-unit'
    search_query = {
        'parallels_uuid': search_results_id,
        'text_ids': [str(found_texts[0].id),
                     str(found_texts[1].id)],
        'unit_type': 'bad-unit'
    }
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert bad_unit in data['message']

    # perform multitext search
    print('Submitting good multitext query')
    search_query = {
        'parallels_uuid': search_results_id,
        'text_ids': [str(found_texts[0].id),
                     str(found_texts[1].id)],
        'unit_type': 'line'
    }
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 201
    assert 'Location' in response.headers
    multitext_results_id = response.headers['Location'].split('/')[-2]

    # wait until multitext search completes
    print('Waiting for multitext results')
    with multitext_app.test_request_context():
        multitext_app.preprocess_request()
        status_endpoint = flask.url_for('multitexts.retrieve_status',
                                        results_id=multitext_results_id)
    response = multitext_client.get(status_endpoint)
    while response.status_code == 404:
        time.sleep(0.1)
        response = multitext_client.get(status_endpoint)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    assert status != tesserae.db.entities.Search.FAILED, data['message']
    while status != tesserae.db.entities.Search.DONE:
        time.sleep(0.1)
        response = multitext_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
        assert status != tesserae.db.entities.Search.FAILED, data['message']

    # make sure we can retrieve multitext results
    print('Retrieving multitext results')
    with multitext_app.test_request_context():
        retrieve_endpoint = flask.url_for('multitexts.retrieve_results',
                                          results_id=multitext_results_id)
    response = multitext_client.get(retrieve_endpoint)
    assert response.status_code == 200, response.data
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'multiresults' in data
    assert len(data['multiresults']) > 0
    for multiresult in data['multiresults']:
        assert 'units' in multiresult
        for unit in multiresult['units']:
            for expected in [
                    'unit_id', 'tag', 'snippet', 'highlight', 'score'
            ]:
                assert expected in unit

    # make sure search results were cached
    print('Verifying that multitext results were cached')
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 303
    assert 'Location' in response.headers
    assert multitext_results_id == response.headers['Location'].split('/')[-2]


def test_multitext_requireds_missing(multitext_app, multitext_client):
    with multitext_app.test_request_context():
        multitext_app.preprocess_request()
        submit_endpoint = flask.url_for('multitexts.submit_multitext')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    search_query = {}
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data


def test_multitext_search_not_found(multitext_app, multitext_client):
    bad_uuid = 'does-not-exist'
    with multitext_app.test_request_context():
        multitext_app.preprocess_request()
        found_texts = flask.g.db.find(tesserae.db.entities.Text.collection)
        submit_endpoint = flask.url_for('multitexts.submit_multitext')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    search_query = {
        'parallels_uuid': bad_uuid,
        'text_ids': [str(found_texts[0].id),
                     str(found_texts[1].id)],
        'unit_type': 'line'
    }
    response = multitext_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert bad_uuid in data['message']
