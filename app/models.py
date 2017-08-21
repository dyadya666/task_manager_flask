from app import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref


class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), index=True, unique=True)

    scores = relationship('Score', backref=backref('score', lazy=False))

    def __repr__(self):
        return '<User id: {0} - name: {1}>'.format(self.id, self.username)


class Score(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    number = Column(Integer, nullable=True)
    progress = Column(String, nullable=True)
    status = Column(String, nullable=True)

    def __repr__(self):
        return '<User with ID "{0}" was guessing number - {1} with next steps {2}>'.\
                format(self.user_id, self.number, self.progress)
