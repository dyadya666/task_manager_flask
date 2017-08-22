from app import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref


class Users(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), index=True, unique=True)

    projects = relationship('Projects', backref=backref('project', lazy=False))

    def __repr__(self):
        return '<User id: {0} - name: {1}>'.format(self.id, self.username)


class Projects(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String, nullable=True)

    def __repr__(self):
        return '<User ID "{0}" - name of project {1}>'.\
                format(self.user_id, self.name)


class Tasks(db.Model):
    pass
