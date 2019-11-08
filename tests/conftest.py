"""Global fixtures for tests"""
from pathlib import Path
import pytest

import flask

import apitess
from tesserae.db.entities import Text
from tesserae.utils import ingest_text


@pytest.fixture(scope='session')
def app():
    cur_app = apitess.create_app({
        'MONGO_HOSTNAME': 'localhost',
        'MONGO_PORT': 27017,
        'MONGO_USER': None,
        'MONGO_PASSWORD': None,
        'DB_NAME': 'test_apitess',
    })

    with cur_app.test_request_context():
        # initialize database for testing
        cur_app.preprocess_request()
        for coll_name in flask.g.db.connection.list_collection_names():
            flask.g.db.connection.drop_collection(coll_name)

    yield cur_app


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


def _get_text_metadata():
    return [
        {
            'cts_urn': 'urn:cts:latinLit:phi0690.phi002',
            'title': 'zaeneid',
            'author': 'zvergil',
            'language': 'latin',
            'year': -19,
            'unit_types': ['line', 'phrase'],
            'path': str(Path(__file__).resolve().parent.joinpath(
                'ztest.aen.tess')),
        },
        {
            'cts_urn': 'urn:cts:latinLit:phi0917.phi001',
            'title': 'zbellum civile',
            'author': 'zlucan',
            'language': 'latin',
            'year': 65,
            'unit_types': ['line', 'phrase'],
            'path': str(Path(__file__).resolve().parent.joinpath(
                'ztest.phar.tess')),
        },
    ]


@pytest.fixture(scope='session')
def populated_app():
    cur_app = apitess.create_app({
        'MONGO_HOSTNAME': 'localhost',
        'MONGO_PORT': 27017,
        'MONGO_USER': None,
        'MONGO_PASSWORD': None,
        'DB_NAME': 'test_apitess_populated',
    })

    with cur_app.test_request_context():
        # initialize populated database for testing
        cur_app.preprocess_request()
        for coll_name in flask.g.db.connection.list_collection_names():
            flask.g.db.connection.drop_collection(coll_name)
        texts_to_add = _get_text_metadata()
        for t in texts_to_add:
            cur_text = Text.json_decode(t)
            text_id = str(ingest_text(flask.g.db, cur_text))

    yield cur_app


@pytest.fixture(scope='session')
def populated_client(populated_app):
    return populated_app.test_client()
