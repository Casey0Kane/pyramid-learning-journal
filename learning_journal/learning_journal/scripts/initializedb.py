import os
import sys
import transaction
from datetime import datetime

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from ..models import Entry


ENTRIES = [
    {
        "id": 0,
        "title": "Test",
        "body": "Isn't sql just so much fun?",
        "creation_date": datetime.strptime("May 30, 2017", "%b %d, %Y")
    },
    {
        "id": 1,
        "title": "Another test",
        "body": "Don't forget jinja!",
        "creation_date": datetime.strptime("May 31, 2017", "%b %d, %Y")
    },
    {
        "id": 2,
        "title": "Stupid bugs",
        "body": "Why are you so complicated?",
        "creation_date": datetime.strptime("Jun 1, 2017", "%b %d, %Y")
    },
]


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        for entry in ENTRIES:
            model = Entry(title=entry['title'],
                          body=entry['body'],
                          creation_date=entry['creation_date'],
                          id=entry['id'])
            dbsession.add_all(model)
