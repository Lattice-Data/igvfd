import os
import pytest
import pkg_resources
import tempfile

from pyramid.paster import get_appsettings


tempfile.tempdir = '/tmp'

pytest_plugins = [
    'igvfd.tests.fixtures.database',
    'igvfd.tests.fixtures.testapp',
    'igvfd.tests.fixtures.alias',
    'igvfd.tests.fixtures.pyramid',
    'igvfd.tests.fixtures.aws',
    'igvfd.tests.fixtures.report',
    'igvfd.tests.fixtures.schemas.access_key',
    'igvfd.tests.fixtures.schemas.lab',
    'igvfd.tests.fixtures.schemas.user',
    'igvfd.tests.fixtures.schemas.page',
    'igvfd.tests.fixtures.schemas.image',
    'igvfd.tests.fixtures.schemas.human_donor',
    'igvfd.tests.fixtures.schemas.controlled_term',
    'igvfd.tests.fixtures.schemas.genetic_modification',
    'igvfd.tests.fixtures.schemas.non_human_donor',
    'igvfd.tests.fixtures.schemas.primary_cell_culture',
    'igvfd.tests.fixtures.schemas.tissue',
    'igvfd.tests.fixtures.schemas.in_vivo_system',
    'igvfd.tests.fixtures.schemas.in_vitro_system',
    'igvfd.tests.fixtures.schemas.plate_based_library',
    'igvfd.tests.fixtures.schemas.droplet_based_library',
    'igvfd.tests.fixtures.schemas.sequence_file',
    'igvfd.tests.fixtures.schemas.tabular_file',
    'igvfd.tests.fixtures.schemas.raw_matrix_file',
    'igvfd.tests.fixtures.schemas.processed_matrix_file',
    'igvfd.tests.fixtures.schemas.sequence_file_set',
]


@pytest.fixture(scope='session')
def ini_file(request):
    path = os.path.abspath(
        request.config.option.ini or 'config/pyramid/ini/testing.ini'
    )
    return get_appsettings(path, name='app')


@pytest.fixture(autouse=True)
def autouse_external_tx(external_tx):
    pass


@pytest.fixture(scope='session')
def app_settings(ini_file, DBSession):
    from snovault import DBSESSION
    ini_file[DBSESSION] = DBSession
    return ini_file


@pytest.fixture(scope='session')
def app(app_settings):
    from igvfd import main
    return main({}, **app_settings)


@pytest.fixture(scope='session')
def workbook(conn, app, app_settings):
    tx = conn.begin_nested()
    try:
        from igvfd.loadxl import load_test_data
        load_test_data(app)
        yield
    finally:
        tx.rollback()
