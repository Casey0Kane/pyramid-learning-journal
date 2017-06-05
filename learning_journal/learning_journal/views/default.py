"""Views for the Learning Journal application."""
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from datetime import date, datetime
from ..models import Entry


@view_config(route_name='home', renderer='../templates/index.jinja2')
def home_view(request):
    """Grab homepage data using jinja."""
    entries = request.dbsession.query(Entry).order_by(Entry.id).all()[::-1]
    latest = entries[0] if entries else ""
    left_entries, right_entries = [], []
    for i in range(1, len(entries)):
        if i % 2:
            left_entries.append(entries[i])
        else:
            right_entries.append(entries[i])
    return {'latest': latest,
            'left_entries': left_entries,
            'right_entries': right_entries}


@view_config(route_name='detail', renderer='../templates/entry.jinja2')
def detail_view(request):
    """Entry for learning journal."""
    e = request.dbsession.query(Entry).get(int(request.matchdict['id']))
    if not e:
        raise HTTPNotFound(detail="Entry does not exist.")
    edit_date = None
    if e.edit_date:
        edit_date = e.edit_date.strftime("%b %d, %Y")
    return {'entry': e, 'edit_date': edit_date}


@view_config(route_name='update', renderer='../templates/edit-entry.jinja2')
def update_view(request):
    """Edit learning journal entry."""
    e = request.dbsession.query(Entry).get(int(request.matchdict['id']))
    if not e:
        raise HTTPNotFound(detail="You cannot edit that which does not exist")
    if request.method == "POST":
        e.title = request.POST['title']
        e.body = request.POST['body']
        e.edit_date = date.today()
        request.dbsession.flush()
        return HTTPFound(location=request.route_url('detail', id=e.id),)
    if request.method == "GET":
        return {'title': e.title, 'body': e.body}


@view_config(route_name='create', renderer='../templates/new-entry.jinja2')
def create_view(request):
    """Create learning journal entry."""
    if request.method == "POST":
        title = request.POST['title']
        body = request.POST['body']
        creation_date = datetime.strptime(request.POST['creation_date'], "%Y-%m-%d")
        entry = Entry(title=title, body=body, creation_date=creation_date)
        request.dbsession.add(entry)
        return HTTPFound(location=request.route_url('home'))
    if request.method == "GET":
        today = date.today()
        return {"creation_date": today}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_tutorial_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
