"""Views for the Learning Journal application."""
from pyramid.response import Response
import io
import os

HERE = os.path.dirname(os.path.dirname(__file__))


def list_view(request):
    """View for the list of journal entries."""
    with io.open(os.path.join(HERE, 'templates/index.html')) as the_file:
        imported_text = the_file.read()
        return Response(imported_text)


def detail_view(request):
    """View for a single journal entry."""
    with io.open(os.path.join(HERE, 'templates/entry.html')) as the_file:
        imported_text = the_file.read()
        return Response(imported_text)


def create_view(request):
    """Create a new view."""
    with io.open(os.path.join(HERE, 'templates/new-entry.html')) as the_file:
        imported_text = the_file.read()
        return Response(imported_text)


def update_view(request):
    """For updating an existing view."""
    with io.open(os.path.join(HERE, 'templates/edit-entry.html')) as the_file:
        imported_text = the_file.read()
        return Response(imported_text)
