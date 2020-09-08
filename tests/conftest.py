"""Global fixtures for tests"""
from pathlib import Path
import tempfile

import flask
import pytest

import apitess
import apitess.texts
from tesserae.db.entities import Text
from tesserae.utils import ingest_text
from tesserae.utils.ingest import IngestQueue
from tesserae.utils.delete import obliterate
from tesserae.utils.coordinate import JobQueue
from tesserae.utils.multitext import BigramWriter

# Write bigram databases to temporary directory
BigramWriter.BIGRAM_DB_DIR = tempfile.mkdtemp()
# Write file uploads to temporary directory
apitess.texts.FILE_UPLOAD_DIR = tempfile.mkdtemp()

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
        jobqueue = JobQueue(1, db_cred)
        ingest_queue = IngestQueue(db_cred)
        cur_app = apitess.create_app(jobqueue, ingest_queue, db_config)

        with cur_app.test_request_context():
            # initialize database for testing
            cur_app.preprocess_request()
            obliterate(flask.g.db)

        yield cur_app
    finally:
        jobqueue.cleanup()
        ingest_queue.cleanup()


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
            'path':
            str(Path(__file__).resolve().parent.joinpath('ztest.aen.tess')),
            'is_prose': False,
        },
        {
            'cts_urn':
            'urn:cts:latinLit:phi0917.phi001',
            'title':
            'zbellum civile',
            'author':
            'zlucan',
            'language':
            'latin',
            'year':
            65,
            'unit_types': ['line', 'phrase'],
            'path':
            str(Path(__file__).resolve().parent.joinpath('ztest.phar.tess')),
            'is_prose':
            False,
        },
        {
            'cts_urn': 'urn:cts:greekLit:tlg0012.tlg001',
            'title': 'ziliad',
            'author': 'zhomer',
            'language': 'greek',
            'year': -750,
            'unit_types': ['line', 'phrase'],
            'path':
            str(Path(__file__).resolve().parent.joinpath('ztest.il.tess')),
            'is_prose': False,
        },
        {
            'cts_urn':
            'urn:cts:greekLit:tlg0059.tlg023.perseus-grc2',
            'title':
            'zgorgias',
            'author':
            'zplato',
            'language':
            'greek',
            'year':
            -283,
            'unit_types': ['line', 'phrase'],
            'path':
            str(Path(__file__).resolve().parent.joinpath('ztest.gorg.tess')),
            'is_prose':
            True,
        },
        {
            'title': 'miniacharnians',
            'author': 'miniaristophanes',
            'language': 'greek',
            'year': -425,
            'path':
            str(Path(__file__).resolve().parent.joinpath('mini.ach.tess')),
            'is_prose': False
        },
        {
            'title':
            'minipunica',
            'author':
            'minisilius',
            'language':
            'latin',
            'year':
            96,
            'path':
            str(Path(__file__).resolve().parent.joinpath('mini.punica.tess')),
            'is_prose':
            False
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
        jobqueue = JobQueue(1, db_populated_cred)
        ingest_queue = IngestQueue(db_cred)
        cur_app = apitess.create_app(jobqueue, ingest_queue,
                                     db_populated_config)

        with cur_app.test_request_context():
            # initialize populated database for testing
            cur_app.preprocess_request()
            obliterate(flask.g.db)
            texts_to_add = _get_text_metadata()
            for t in texts_to_add:
                cur_text = Text.json_decode(t)
                ingest_text(flask.g.db, cur_text)

        yield cur_app

        with cur_app.test_request_context():
            # delete populated test database
            cur_app.preprocess_request()
            obliterate(flask.g.db)
    finally:
        jobqueue.cleanup()
        ingest_queue.cleanup()


@pytest.fixture(scope='session')
def populated_client(populated_app):
    return populated_app.test_client()


db_multitext_config = {
    'MONGO_HOSTNAME': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_USER': None,
    'MONGO_PASSWORD': None,
    'DB_NAME': 'test_apitess_multitext',
}

db_multitext_cred = {
    'host': db_multitext_config['MONGO_HOSTNAME'],
    'port': db_multitext_config['MONGO_PORT'],
    'user': db_multitext_config['MONGO_USER'],
    'password': db_multitext_config['MONGO_PASSWORD'],
    'db': db_multitext_config['DB_NAME']
}


@pytest.fixture(scope='session')
def multitext_app():
    try:
        jobqueue = JobQueue(1, db_multitext_cred)
        ingest_queue = IngestQueue(db_cred)
        cur_app = apitess.create_app(jobqueue, ingest_queue,
                                     db_multitext_config)

        with cur_app.test_request_context():
            # initialize multitext database for testing
            cur_app.preprocess_request()
            obliterate(flask.g.db)
            texts_to_add = _get_text_metadata()
            for t in texts_to_add:
                cur_text = Text.json_decode(t)
                ingest_text(flask.g.db, cur_text, enable_multitext=True)

        yield cur_app

        with cur_app.test_request_context():
            # delete multitext test database
            cur_app.preprocess_request()
            obliterate(flask.g.db)
    finally:
        jobqueue.cleanup()
        ingest_queue.cleanup()


@pytest.fixture(scope='session')
def multitext_client(multitext_app):
    return multitext_app.test_client()
