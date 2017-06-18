import pytest
import transaction
import os
from .models import Entry, get_tm_session
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from zope.interface.interfaces import ComponentLookupError
from .models.meta import Base
from pyramid import testing
from pyramid.security import Allow, Everyone, Authenticated
from passlib.apps import custom_app_context as context
import faker
import contextlib
import datetime


fake = faker.Faker()

ENTRIES = [Entry(
    title=fake.catch_phrase(),
    body=fake.paragraph(),
    creation_date=fake.date_object(),
    edit_date=fake.date_object()
) for i in range(99)] + [Entry(
    title="Test",
    body='Sample body',
    creation_date=fake.date_object()
)]


ROUTES = ['/',
          '/journal/new-entry',
          '/journal/1',
          '/journal/1/edit-entry']


class DummyAuthenticationPolicy(object):
    def __init__(self, userid):
        self.userid = userid

    def authenticated_userid(self, request):
        return self.userid

    def unauthenticated_userid(self, request):
        return self.userid

    def effective_principals(self, request):
        principals = [Everyone]
        if self.userid:
            principals += [Authenticated]
        return principals

    def remember(self, request, userid, **kw):
        return []

    def forget(self, request):
        return []


@contextlib.contextmanager
def set_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


@pytest.fixture(scope="session")
def configuration(request):
    """Return config for a db_session."""
    settings = {'sqlalchemy.url': 'postgres://localhost:5432/learning_journal'}
    config = testing.setUp(settings=settings)
    config.include('learning_journal.models')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture
def db_session(configuration, request):
    """Return a db_session."""
    session_factory = configuration.registry['dbsession_factory']
    session = session_factory()
    engine = session.bind
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Test dummy request fixture."""
    return testing.DummyRequest(dbsession=db_session)


@pytest.fixture
def add_models(dummy_request):
    """Add models to dummy request."""
    dummy_request.dbsession.add_all(ENTRIES)


# Unit Tests #


def test_entries_are_added(db_session):
    """Test all entries are added to database."""
    db_session.add_all(ENTRIES)
    query = db_session.query(Entry).all()
    assert len(query) == len(ENTRIES)


def test_home_view_filled(dummy_request, add_models):
    """Test home_view returns all entries."""
    from .views.default import home_view
    res = home_view(dummy_request)
    entries = res['left_entries'] + res['right_entries'] + [res['latest']]
    assert len(entries) == len(ENTRIES)


def test_detail_view(dummy_request, add_models):
    """Test detail page for first entry."""
    from .views.default import detail_view
    dummy_request.matchdict['id'] = 1
    res = detail_view(dummy_request)
    assert res['entry'].title == ENTRIES[0].title


def test_detail_view_not_found(dummy_request):
    """Test 404 not found for detail."""
    from .views.default import detail_view
    dummy_request.matchdict['id'] = 1
    with pytest.raises(Exception):
        detail_view(dummy_request)


def test_update_view(dummy_request, add_models):
    """Test update view has dummy request."""
    from .views.default import update_view
    dummy_request.matchdict['id'] = 1
    res = update_view(dummy_request)
    assert res['title'] == ENTRIES[0].title
    assert res['body'] == ENTRIES[0].body


def test_update_view_not_found(dummy_request):
    """Test update view for a non-existant entry."""
    from .views.default import update_view
    dummy_request.matchdict['id'] = 1
    with pytest.raises(Exception):
        update_view(dummy_request)


def test_update_view_post(dummy_request, add_models):
    """Test ability to update db."""
    from .views.default import update_view
    dummy_request.matchdict['id'] = 2
    dummy_request.method = 'POST'
    dummy_request.POST['title'] = 'test'
    dummy_request.POST['body'] = 'oh yes test'
    try:
        update_view(dummy_request)
    except ComponentLookupError:
        pass
    entry = dummy_request.dbsession.query(Entry).get(2)
    assert entry.title == 'test'
    assert entry.body == 'oh yes test'


def test_create_view_get(dummy_request):
    """Test create view initial get."""
    from .views.default import create_view
    res = create_view(dummy_request)
    assert type(res['creation_date']) is datetime.date


def test_create_view_post(dummy_request):
    """Test create view form submission adds to db."""
    from .views.default import create_view
    dummy_request.method = 'POST'
    dummy_request.POST['title'] = 'Tester'
    dummy_request.POST['body'] = 'test test test'
    dummy_request.POST['creation_date'] = '2020-01-01'
    try:
        create_view(dummy_request)
    except ComponentLookupError:
        pass
    entry = dummy_request.dbsession.query(Entry).first()
    assert entry.title == 'Tester'
    assert entry.body == 'test test test'
    assert 'datetime' in str(type(entry.creation_date))


def test_check_credentials_invalid():
    """Test check credentials returns false for invalid username and pass."""
    from .security import check_credentials
    assert check_credentials('potato', '') is False
    assert check_credentials('kittens', 'password') is False
    assert check_credentials('dagnabit', 'password') is False


# Functional Tests #


@pytest.fixture
def testapp():
    """Return mock app."""
    from webtest import TestApp
    from pyramid.config import Configurator

    def main(global_config, **settings):
        """The function returns a Pyramid WSGI application."""
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('learning_journal.models')
        config.include('learning_journal.routes')
        config.include('learning_journal.security')
        config.scan()
        return config.make_wsgi_app()

    app = main({}, **{"sqlalchemy.url": "postgres://localhost:5432/learning_journal"})
    testapp = TestApp(app)
    session_factory = app.registry["dbsession_factory"]
    engine = session_factory().bind
    Base.metadata.create_all(bind=engine)

    return testapp


@pytest.fixture
def fill_db(testapp):
    """Fill database."""
    session_factory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        dbsession.add_all(ENTRIES)


def test_home_has_list(testapp):
    """Test home view has list."""
    response = testapp.get('/', status=200)
    assert str(response.html).count('div class="one-half column"') == 2


def test_home_route_with_data_has_all_articles(testapp, fill_db):
    """Test all articles are rendered."""
    response = testapp.get('/', status=200)
    assert len(response.html.find_all('article')) == 100


def test_detail_page(testapp, fill_db):
    """Test detail page renders correctly."""
    response = testapp.get('/journal/100', status=200).html
    assert response.find('h4').text == 'Test'
    assert response.find('p').text == 'Sample body'


@pytest.fixture(scope="function")
def login(testapp):
    """Authenticate testapp session."""
    os.environ["AUTH_PASSWORD"] = context.hash('password')
    os.environ["AUTH_USERNAME"] = 'Coffee'
    post_params = {
        'username': 'Coffee',
        'password': 'password'
    }
    testapp.post('/login', post_params)


def test_login_view_post(testapp, login):
    """Test login view."""
    pswrd = context.hash('password')
    with set_env(AUTH_PASSWORD=pswrd):
        post_params = {
            'password': 'password',
            'username': 'Coffee'
        }
        res = testapp.post('/login', post_params)
        assert res.headers['Location'] == 'http://localhost/'


def test_logout_view(testapp):
    """Test that logout works."""
    response = testapp.get('/logout').follow()
    assert response
