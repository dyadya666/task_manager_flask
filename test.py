#!myvenv/bin/python3

from coverage import coverage

cov = coverage(branch=True, omit=['myvenv/*', 'test.py'])
cov.start()

import os
import unittest
import json

from flask_login import login_user
from config import basedir
from app import app, db, views, log_manager
from app.models import Users, Projects, Tasks, COMPLETE, IN_PROGRESS


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        app.config['CSRF_ENABLED'] =False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                os.path.join(basedir, 'test.db')
        log_manager.init_app(app)
        self.app =  app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # def test_view(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/view/Sergey', content_type='html/text')
    #     self.assertAlmostEqual(response.status_code, 302)

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

        project = views.create_project(name='new_project',
                                       user_id=user.id,
                                       test=True)
        self.assertEqual(project.name, 'new_project')

    def test_delete_project(self):
        user = Users(nickname='ivan')
        db.session.add(user)
        db.session.commit()
        project = Projects(name='new project', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        result = views.delete_project(id=project.id, user_id=user.id, test=True)

        self.assertEqual(result, True)



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
