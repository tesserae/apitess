import csv
import gzip
import io
import json
import time

import flask
import tesserae.db.entities
import werkzeug.datastructures


def test_greek_to_latin(populated_app, populated_client):
    # request a search
    print('Submitting search')
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        found_texts = {
            t.title: t
            for t in flask.g.db.find(tesserae.db.entities.Text.collection)
        }
        submit_endpoint = flask.url_for('parallels.submit_search')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    search_query = {
        'source': {
            'object_id': str(found_texts['miniacharnians'].id),
            'units': 'line'
        },
        'target': {
            'object_id': str(found_texts['minipunica'].id),
            'units': 'line'
        },
        'method': {
            'name': 'greek_to_latin',
            'greek_stopwords': [],
            'latin_stopwords': ['et', 'non', 'iam'],
            'freq_basis': 'corpus',
            'max_distance': 999,
            'distance_basis': 'frequency',
            'min_score': 0
        }
    }
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 201
    assert 'Location' in response.headers
    search_results_id = response.headers['Location'].split('/')[-2]

    # wait until search completes
    print('Waiting for search to complete')
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        status_endpoint = flask.url_for('parallels.retrieve_status',
                                        results_id=search_results_id)
    response = populated_client.get(status_endpoint)
    while response.status_code == 404:
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    assert status != tesserae.db.entities.Search.FAILED, data['message']
    while status != tesserae.db.entities.Search.DONE:
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
        assert status != tesserae.db.entities.Search.FAILED, data['message']
    # current response should have everything at 100%
    for progress_entry in data['progress']:
        assert progress_entry['value'] == 1.0
    print(search_results_id)
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        print(flask.g.db.find('searches', results_id=search_results_id))

    # make sure we can retrieve results
    print('Retrieving search results')
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id)
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert len(data['parallels']) > 0

    # make sure search results were cached
    print('Verifying that search results were cached')
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 303
    assert 'Location' in response.headers
    assert search_results_id == response.headers['Location'].split('/')[-2]


def test_min_score(populated_app, populated_client):
    # request a search
    print('Submitting search')
    with populated_app.test_request_context():
        populated_app.preprocess_request()
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
            'distance_basis': 'frequency',
            'min_score': 2.5
        }
    }
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 201
    assert 'Location' in response.headers
    search_results_id = response.headers['Location'].split('/')[-2]

    # wait until search completes
    print('Waiting for search to complete')
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        status_endpoint = flask.url_for('parallels.retrieve_status',
                                        results_id=search_results_id)
    response = populated_client.get(status_endpoint)
    while response.status_code == 404:
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    assert status != tesserae.db.entities.Search.FAILED, data['message']
    while status != tesserae.db.entities.Search.DONE:
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
        assert status != tesserae.db.entities.Search.FAILED, data['message']
    # current response should have everything at 100%
    for progress_entry in data['progress']:
        assert progress_entry['value'] == 1.0

    # make sure we can retrieve results
    print('Retrieving search results')
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id)
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert len(data['parallels']) > 0

    # make sure search results were cached
    print('Verifying that search results were cached')
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 303
    assert 'Location' in response.headers
    assert search_results_id == response.headers['Location'].split('/')[-2]


def test_search_search_retrieval(populated_app, populated_client):
    # request a search
    print('Submitting search')
    with populated_app.test_request_context():
        populated_app.preprocess_request()
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
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 201
    assert 'Location' in response.headers
    search_results_id = response.headers['Location'].split('/')[-2]

    # wait until search completes
    print('Waiting for search to complete')
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        status_endpoint = flask.url_for('parallels.retrieve_status',
                                        results_id=search_results_id)
    response = populated_client.get(status_endpoint)
    while response.status_code == 404:
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    assert status != tesserae.db.entities.Search.FAILED, data['message']
    while status != tesserae.db.entities.Search.DONE:
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
        assert status != tesserae.db.entities.Search.FAILED, data['message']
    # current response should have everything at 100%
    for progress_entry in data['progress']:
        assert progress_entry['value'] == 1.0

    # make sure we can retrieve results
    print('Retrieving search results')
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id)
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert len(data['parallels']) > 0

    # make sure search results were cached
    print('Verifying that search results were cached')
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 303
    assert 'Location' in response.headers
    assert search_results_id == response.headers['Location'].split('/')[-2]

    # make sure redirect URL to cached results works
    redirect_url = response.headers['Location']
    response = populated_client.get(redirect_url)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert 'max_score' in data
    assert 'total_count' in data

    # try various paging options
    print('Retrieve everything')
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id)
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert 'max_score' in data
    assert 'total_count' in data
    parallels = data['parallels']
    assert len(parallels) == int(data['total_count'])
    assert max(p['score'] for p in parallels) == float(data['max_score'])

    print('Retrieving by score')
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id,
                                          sort_by='score',
                                          sort_order='descending',
                                          per_page='3',
                                          page_number='0')
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert 'max_score' in data
    assert 'total_count' in data
    parallels = data['parallels']
    assert len(parallels) == 3
    for earlier, later in zip(parallels[:-1], parallels[1:]):
        assert earlier['score'] >= later['score']

    print('Retrieving by source_tag')
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id,
                                          sort_by='source_tag',
                                          sort_order='ascending',
                                          per_page='3',
                                          page_number='0')
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    assert 'max_score' in data
    assert 'total_count' in data
    parallels = data['parallels']
    assert len(parallels) == 3
    for earlier, later in zip(parallels[:-1], parallels[1:]):
        assert tuple(earlier['source_tag'].split()[-1].split('.')) <= \
            tuple(later['source_tag'].split()[-1].split('.'))
    print('Try ridiculous page')
    with populated_app.test_request_context():
        retrieve_endpoint = flask.url_for('parallels.retrieve_results',
                                          results_id=search_results_id,
                                          sort_by='target_tag',
                                          sort_order='descending',
                                          per_page='999999999',
                                          page_number='999999999')
    response = populated_client.get(retrieve_endpoint)
    assert response.status_code == 200
    data = flask.json.loads(
        gzip.decompress(response.get_data()).decode('utf-8'))
    assert 'parallels' in data
    parallels = data['parallels']
    assert len(parallels) == 0

    print('Try downloading')
    with populated_app.test_request_context():
        download_endpoint = flask.url_for('parallels.download',
                                          results_id=search_results_id)
    response = populated_client.get(download_endpoint)
    assert response.status_code == 200
    assert 'Content-Disposition' in response.headers
    assert search_results_id in response.headers['Content-Disposition']
    data = gzip.decompress(response.get_data()).decode('utf-8')
    with io.StringIO(initial_value=data, newline='') as ifh:
        reader = csv.reader(ifh, delimiter='\t')
        rows = [row for row in reader]
        assert len(rows) > 0
        row_count = 0
        for row in rows:
            if not row[0].startswith('#'):
                # ignore commented rows
                row_count += 1
        # there are 4 results, plus a header
        assert row_count == 5


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
            # !!! bad feature
            'feature': bad_feature,
            'stopwords': ['et', 'qui', 'quis'],
            'score_basis': 'lemmata',
            'freq_basis': 'corpus',
            'max_distance': 6,
            'distance_basis': 'frequency'
        }
    }
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
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
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
    assert response.status_code == 200
    data = response.get_json()
    status = data['status']
    while status != tesserae.db.entities.Search.FAILED:
        time.sleep(0.1)
        response = populated_client.get(status_endpoint)
        data = response.get_json()
        status = data['status']
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
        'source': {
            'object_id': str(found_texts[0].id),
            'units': 'line'
        },
        'target': {
            'object_id': str(found_texts[1].id),
            'units': 'line'
        },
    }
    response = populated_client.post(submit_endpoint,
                                     data=json.dumps(search_query),
                                     headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    for k1, v1 in search_query.items():
        assert k1 in data['data']
        rv1 = data['data'][k1]
        for k2, v2 in v1.items():
            assert k2 in rv1
            assert rv1[k2] == v2
    assert 'method' in data['message'].split(': ')[-1].split(',')


def test_search_no_body(populated_app, populated_client):
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        submit_endpoint = flask.url_for('parallels.submit_search')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    response = populated_client.post(submit_endpoint,
                                     data=None,
                                     headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data['data'] == ''
    assert data['message'] == 'No search parameters were sent with the request'


def test_search_unparsable_body(populated_app, populated_client):
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        submit_endpoint = flask.url_for('parallels.submit_search')
    headers = werkzeug.datastructures.Headers()
    headers['Content-Type'] = 'application/json; charset=utf-8'
    unparsable = 'Bound to fail'
    response = populated_client.post(submit_endpoint,
                                     data=unparsable,
                                     headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data['data'] == unparsable
    assert data['message'].startswith('Unable to parse search parameters')
    assert 'JSON data is malformed' in data['message']


def test_search_bad_content_type(populated_app, populated_client):
    with populated_app.test_request_context():
        populated_app.preprocess_request()
        submit_endpoint = flask.url_for('parallels.submit_search')
    headers = werkzeug.datastructures.Headers()
    original_data = '{"garbage": "data"}'
    response = populated_client.post(submit_endpoint,
                                     data=original_data,
                                     headers=headers)
    print(response.headers['Content-Type'])
    assert response.status_code == 400
    data = response.get_json()
    assert data['data'] == original_data
    assert data['message'].startswith('Unable to parse search parameters')
    assert 'Content-Type' in data['message']
