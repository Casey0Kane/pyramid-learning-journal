from pyramid import testing
from pyramid.response import Response
import pytest


@pytest.fixture
def list_view_response():
    """Return a response for a home page."""
    from expense_tracker.views.default import list_view
    request = testing.DummyRequest()
    response = list_view(request)
    return response


def test_list_view_returns_response_given_request(list_view):
    """Home view returns a response object when given a request."""
    assert isinstance(list_view, Response)


def test_list_view_is_good(list_view):
    """Test that the home view is 200 response OK."""
    assert list_view.status_code == 200
