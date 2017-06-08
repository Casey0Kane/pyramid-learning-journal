from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    Date
)

from .meta import Base


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    body = Column(Unicode)
    creation_date = Column(Date)
    edit_date = Column(Date)

    def to_json(self):
    return {
        "id": self.id,
        "title": self.title,
        "body": self.body,
        "creation_date": self.creation_date,
        "edit_date": self.edit_date
    }