"""Views for the Learning Journal application."""
from pyramid.response import Response
import io
import os

HERE = os.path.dirname(__file__)


def list_view():
    """View for the list of journal entries."""
    with io.open(os.path.join(HERE, 'index.html')) as the_file:
        imported_text = the_file.read()
        the_file.close()
        return Response(imported_text)


def detail_view():
    """View for a single journal entry."""
    with io.open(os.path.join(HERE, 'entry.html')) as the_file:
        imported_text = the_file.read()
        the_file.close()
        return Response(imported_text)


def create_view():
    """Create a new view."""
    with io.open(os.path.join(HERE, 'new-entry.html')) as the_file:
        imported_text = the_file.read()
        the_file.close()
        return Response(imported_text)


def update_view():
    """For updating an existing view."""
    with io.open(os.path.join(HERE, 'edit-entry.html')) as the_file:
        imported_text = the_file.read()
        the_file.close()
        return Response(imported_text)
