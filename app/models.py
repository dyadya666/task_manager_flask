from app import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref


IN_PROGRESS = 'inprogress'
COMPLETE = 'completed'


class Users(db.Model):
    id = Column(Integer, primary_key=True)
    nickname = Column(String(50), index=True, unique=True)

    projects = relationship('Projects', backref=backref('projects', lazy=False))

    def __repr__(self):
        return '<User id: {0} - nickname: {1}>'.format(self.id, self.nickname)


class Projects(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=True)

    tasks = relationship('Tasks', backref=backref('tasks', lazy=False))

    def __repr__(self):
        return '<User ID "{0}" - name of project {1}>'.\
                format(self.user_id, self.name)


class Tasks(db.Model):
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    name = Column(String, index=True)
    status = Column(String, default=IN_PROGRESS)
    deadline = Column(String, nullable=True)
    priority = Column(Integer, default=0)

    project = relationship(Projects, backref=backref('children', cascade='all, delete, delete-orphan'))

    def __repr__(self):
        return 'Project ID: {0}; name: "{1}"; priority: {2}; status: "{3}"'.\
            format(self.project_id, self.name, self.priority, self.status)
