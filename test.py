#!myvenv/bin/python3

from coverage import coverage

cov = coverage(branch=True, omit=['myvenv/*', 'test.py'])
cov.start()

import os
import unittest

from config import basedir
from app import app, db
from app.models import Users, Projects, Tasks, COMPLETE, IN_PROGRESS


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] =False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                os.path.join(basedir, 'test.db')
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        user = Users(nickname='ivan')
        db.session.add(user)
        db.session.commit()
        assert user.is_authenticated() == True
        assert user.is_active() == True
        assert user.is_anonymous() == False
        assert user.id == int(user.get_id())

    def test_create_project(self):
        user = Users(nickname='ivan')
        db.session.add(user)
        db.session.commit()

        project = Projects(name='new project', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        assert project.name == 'new project'
        assert project.user_id == user.id

    def test_delete_project(self):
        user = Users(nickname='ivan')
        project = Projects(name='new project', user_id=user.id)
        db.session.add(project)
        db.session.add(user)
        db.session.commit()

        db.session.delete(project)
        db.session.commit()
        project = Projects.query.filter_by(name='new_project').first()

        assert project == None



if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass

    cov.stop()
    cov.save()

    print('\n\nCoverage report:\n')
    cov.report()
    print('HTML version: ' + os.path.join(basedir, 'tmp/coverage/index.html'))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
