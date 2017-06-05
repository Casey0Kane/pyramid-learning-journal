"""Views for the Learning Journal application."""
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from learning_journal.data import JOURNALS


@view_config(
    route_name='home',
    renderer='../templates/index.jinja2'
)
def list_view(request):
    """View for the list of journal entries."""
    return {
        'id': '',
        'title': '',
        'creation_date': '',
        'body': '',
    }


@view_config(
    route_name="entry",
    renderer='../templates/entry.jinja2'
)
def detail_view(request):
    """View for a single journal entry."""
    the_id = int(request.matchdict['id'])
    try:
        journals = JOURNALS[the_id]
    except IndexError:
        raise HTTPNotFound
    return {
        'journals': journals
    }


@view_config(
    route_name="create",
    renderer='../templates/new-entry.jinja2'
)
def create_view(request):
    """Create a new view."""
    pass


@view_config(
    route_name='edit',
    renderer='../templates/edit-entry.jinja2'
)
def update_view(request):
    """For updating an existing view."""
    pass
