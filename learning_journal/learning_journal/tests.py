import pytest
from pyramid import testing


@pytest.fixture
def req():
    """Return dummy request."""
    req = testing.DummyRequest()
    return req


@pytest.fixture
def testapp():
    """Return mock app."""
    from webtest import TestApp
    from learning_journal import main
    app = main({})
    return TestApp(app)


@pytest.fixture(params=['/',
                        '/journal/2',
                        '/journal/new-entry',
                        '/journal/2/edit-entry'])
def test_response(request):
    """Return test responses."""
    from webtest import TestApp
    from learning_journal import main
    app = main({})
    testapp = TestApp(app)
    response = testapp.get(request.param, status=200)
    return response


def test_home_view_renders_home_data(req):
    """My home page view returns dictionary."""
    from .views.default import home_view
    response = home_view(req)
    assert 'latest' in response
    assert 'left_entries' in response
    assert 'right_entries' in response


def test_home_has_iterables(req):
    """Test home view response returns iterable(dictionary)."""
    from .views.default import home_view
    response = home_view(req)
    assert hasattr(response['left_entries'], '__iter__')
    assert hasattr(response['right_entries'], '__iter__')


def test_home_has_list(testapp):
    response = testapp.get('/', status=200)
    inner_html = response.html
    assert str(inner_html).count('div class="one-half column"') == 2


def test_home_css_links(test_response):
    inner_html = test_response.html
    print(inner_html)
    assert str(inner_html).count('text/css') == 3
