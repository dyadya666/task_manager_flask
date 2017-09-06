#!myvenv/bin/python3

from coverage import coverage

cov = coverage(branch=True, omit=['myvenv/*', 'test.py'])
cov.start()

import os
import unittest

from config import basedir
from app import app, db, views, log_manager
from app.models import Users, Projects, Tasks, IN_PROGRESS


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
        project = Projects(name='new_project', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        result = views.delete_project(id=project.id, user_id=user.id, test=True)

        self.assertEqual(result, True)

    def test_update_project(self):
        user = Users(nickname='ivan')
        db.session.add(user)
        db.session.commit()
        project = Projects(name='new_project', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        result = views.update_project(id=project.id,
                                      user_id=user.id,
                                      new_name='new_name_of_project',
                                      test=True)

        self.assertEqual(result, True)

    def test_change_priority(self):
        first_task = Tasks(name='first_task', project_id=1)
        second_task = Tasks(name='second_task', project_id=1)
        db.session.add(first_task)
        db.session.add(second_task)
        db.session.commit()
        #down
        result_down = views.change_priority(id_task_to_move=first_task.id,
                                            project_id=first_task.project_id,
                                            up_down='down',
                                            test=True)
        #lower
        result_lower = views.change_priority(id_task_to_move=first_task.id,
                                             project_id=first_task.project_id,
                                             up_down='down',
                                             test=True)
        #up
        result_up = views.change_priority(id_task_to_move=first_task.id,
                                          project_id=first_task.project_id,
                                          up_down='up',
                                          test=True)
        #higher
        result_higher = views.change_priority(id_task_to_move=first_task.id,
                                              project_id=first_task.project_id,
                                              up_down='up',
                                              test=True)
        self.assertEqual(result_down, True)
        self.assertEqual(result_up, True)
        self.assertEqual(result_higher, True)
        self.assertEqual(result_lower, True)

    def test_create_task(self):
        result = views.create_task(new_task_name='new_task', project_id=1, test=True)

        self.assertEqual(result, True)

    def test_delete_task(self):
        task = Tasks(name='new_task', project_id=1)
        db.session.add(task)
        db.session.commit()

        result = views.delete_task(id=task.id,
                                   project_id=task.project_id,
                                   test=True)

        self.assertEqual(result, True)

    def test_update_task(self):
        task = Tasks(name='old_name', project_id=1, deadline='2017/09/01')
        db.session.add(task)
        db.session.commit()
        old_name = task.name
        old_deadline = task.deadline

        result = views.update_task(id=task.id,
                                   project_id=1,
                                   new_name='new_name',
                                   deadline='2017/10/03',
                                   test=True)
        self.assertEqual(result, True)
        self.assertEqual(old_name, 'old_name')
        self.assertEqual(old_deadline, '2017/09/01')

    def test_task_done(self):
        task = Tasks(name='new_name', project_id=1)
        db.session.add(task)
        db.session.commit()

        old_status = task.status

        result_tick = views.task_done(task_id=task.id,
                                 project_id=1,
                                 status_checkbox='true',
                                 test=True)
        result_unmark = views.task_done(task_id=task.id,
                                      project_id=1,
                                      status_checkbox='',
                                      test=True)
        self.assertEqual(old_status, IN_PROGRESS)
        self.assertEqual(result_tick, True)
        self.assertEqual(result_unmark, True)


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
