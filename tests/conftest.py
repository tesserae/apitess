"""Global fixtures for tests"""
from pathlib import Path
import tempfile

import flask
import pytest

import apitess
from tesserae.db.entities import Text
from tesserae.utils import ingest_text
from tesserae.utils.search import AsynchronousSearcher
from tesserae.utils.multitext import BigramWriter


# Write bigram databases to temporary directory
BigramWriter.BIGRAM_DB_DIR = tmpfile.TemporaryDirectory()


db_config = {
    'MONGO_HOSTNAME': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_USER': None,
    'MONGO_PASSWORD': None,
    'DB_NAME': 'test_apitess',
}

db_cred = {
    'host': db_config['MONGO_HOSTNAME'],
    'port': db_config['MONGO_PORT'],
    'user': db_config['MONGO_USER'],
    'password': db_config['MONGO_PASSWORD'],
    'db': db_config['DB_NAME']
}


@pytest.fixture(scope='session')
def app():
    try:
        a_searcher = AsynchronousSearcher(1, db_cred)
        cur_app = apitess.create_app(a_searcher, db_config)

        with cur_app.test_request_context():
            # initialize database for testing
            cur_app.preprocess_request()
            for coll_name in flask.g.db.connection.list_collection_names():
                flask.g.db.connection.drop_collection(coll_name)

        yield cur_app
    finally:
        a_searcher.cleanup()


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
        {
            'cts_urn': 'urn:cts:greekLit:tlg0012.tlg001',
            'title': 'ziliad',
            'author': 'zhomer',
            'language': 'greek',
            'year': -750,
            'unit_types': ['line', 'phrase'],
            'path': str(Path(__file__).resolve().parent.joinpath(
                'ztest.il.tess')),
        },
        {
            'cts_urn': 'urn:cts:greekLit:tlg0059.tlg023.perseus-grc2',
            'title': 'zgorgias',
            'author': 'zplato',
            'language': 'greek',
            'year': -283,
            'unit_types': ['line', 'phrase'],
            'path': str(Path(__file__).resolve().parent.joinpath(
                'ztest.gorg.tess')),
        },
    ]


db_populated_config = {
    'MONGO_HOSTNAME': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_USER': None,
    'MONGO_PASSWORD': None,
    'DB_NAME': 'test_apitess_populated',
}

db_populated_cred = {
    'host': db_populated_config['MONGO_HOSTNAME'],
    'port': db_populated_config['MONGO_PORT'],
    'user': db_populated_config['MONGO_USER'],
    'password': db_populated_config['MONGO_PASSWORD'],
    'db': db_populated_config['DB_NAME']
}

@pytest.fixture(scope='session')
def populated_app():
    try:
        a_searcher = AsynchronousSearcher(1, db_populated_cred)
        cur_app = apitess.create_app(a_searcher, db_populated_config)

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
    finally:
        a_searcher.cleanup()


@pytest.fixture(scope='session')
def populated_client(populated_app):
    return populated_app.test_client()
