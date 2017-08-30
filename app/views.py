from flask_login import login_user, logout_user, current_user, login_required, \
                        UserMixin
from flask import render_template, redirect, url_for, request, jsonify, g
from sqlalchemy import func

from app import app, db, open_id, log_manager
from .forms import LoginForm
from .models import Users, Projects, Tasks, COMPLETE, IN_PROGRESS


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@open_id.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('view'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(nickname=form.nickname.data).first()

        if user is None:
            user = Users(nickname=form.nickname.data)
            db.session.add(user)
            db.session.commit()

        user = get_user(id=user.id)
        login_user(user)
        return redirect(request.args.get('next') or url_for('view', nickname=g.user.nickname))
    return render_template('login.html',
                           title='Log In',
                           form=form,
                           error=open_id.fetch_error())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/view/<nickname>')
@login_required
def view(nickname):
    user = g.user
    projects = Projects.query.filter_by(user_id=user.id).all()
    for project in projects:
        tasks = project.tasks
        tasks_sorted = sorted(tasks, key=lambda tasks: tasks.priority)
        project.tasks = tasks_sorted
    return render_template('view.html',
                           title='List',
                           user=user,
                           projects=projects)


class User(UserMixin):
    def __init__(self, nickname, id, active=True):
        self.nickname = nickname
        self.id = id
        self.active = active

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


@log_manager.user_loader
def get_user(id):
    user = Users.query.get(id)
    return User(user.nickname, user.id)


# API for Projects
@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    new_project = Projects(name=request.form['name'], user_id=g.user.id)
    db.session.add(new_project)
    db.session.commit()

    check = Projects.query.filter_by(user_id=g.user.id,
                                    name=request.form['name']).first()
    if check is None:
        return jsonify({
            'result': False
        })
    return jsonify({
        'result': True
    })


@app.route('/delete_project', methods=['POST'])
@login_required
def delete_project():
    project = Projects.query.filter_by(id=request.form['project_id'],
                                       user_id=g.user.id).first()
    db.session.delete(project)
    db.session.commit()

    try:
        Projects.query.filter_by(id=request.form['id'],
                                 user_id=g.user.id).first()
        return jsonify({
            'result': False
        })
    except:
        return jsonify({
            'result': True
        })


@app.route('/update_project', methods=['POST'])
@login_required
def update_project():
    project = Projects.query.filter_by(id=request.form['project_id'],
                                       user_id=g.user.id).first()
    project.name = request.form['new_name']
    db.session.add(project)
    db.session.commit()

    check = Projects.query.filter_by(id=request.form['project_id'],
                                     user_id=g.user.id).first()
    if check.name == request.form['new_name']:
        return jsonify({
            'result': True
        })

    return jsonify({
        'result': False
    })


@app.route('/change_priority', methods=['POST'])
@login_required
def change_priority():
    task_to_move = Tasks.query.filter_by(id=request.form['task_id'],
                                         project_id=request.form['project_id']).first()
    list_of_priority = set_priority(request.form['project_id'])

    if request.form['up_down'] == 'up':
        if list_of_priority.index(task_to_move.priority) - 1 < 0:
            return jsonify({
                'result': True
            })

        priority_of_previous_task = list_of_priority[list_of_priority.index(task_to_move.priority)] - 1
        previous_task = Tasks.query.filter_by(project_id=request.form['project_id'],
                                              priority=priority_of_previous_task).first()
        previous_task.priority = task_to_move.priority
        task_to_move.priority = priority_of_previous_task
        db.session.add(task_to_move)
        db.session.add(previous_task)
        try:
            db.session.commit()
            return jsonify({
                'result': True
            })
        except:
            return jsonify({
                'result': False
            })

    if request.form['up_down'] == 'down':
        try:
            priority_of_next_task = list_of_priority[list_of_priority.index(task_to_move.priority) + 1]
        except IndexError:
            db.session.commit()
            return jsonify({
                'result': True
            })

        next_task = Tasks.query.filter_by(project_id=request.form['project_id'],
                                              priority=priority_of_next_task).first()
        next_task.priority = task_to_move.priority
        task_to_move.priority = priority_of_next_task
        db.session.add(task_to_move)
        db.session.add(next_task)
        try:
            db.session.commit()
            return jsonify({
                'result': True
            })
        except:
            return jsonify({
                'result': False
            })


# API for Tasks
@app.route('/create_task', methods=['POST'])
@login_required
def create_task():
    new_task = Tasks(name=str(request.form['new_name']).strip(),
                     project_id=request.form['project_id'])
    list_of_priority = set_priority(request.form['project_id'])
    list_of_priority.reverse()
    try:
        new_task.priority = list_of_priority[0] + 1
        db.session.add(new_task)
        db.session.commit()
    except IndexError:
        db.session.add(new_task)
        db.session.commit()

    check = Tasks.query.filter_by(name=request.form['new_name'],
                                  project_id=request.form['project_id']).first()
    if check is None:
        return jsonify({
            'result': False
        })
    return jsonify({
        'result': True
    })


def set_priority(project_id):
    tasks = Tasks.query.filter_by(project_id=project_id).all()
    list_of_priorities = [task.priority for task in tasks]
    list_of_priorities.sort()

    return list_of_priorities


@app.route('/delete_task', methods=['POST'])
@login_required
def delete_task():
    task = Tasks.query.filter_by(id=request.form['task_id'],
                                 project_id=request.form['project_id']).first()
    db.session.delete(task)
    db.session.commit()

    check = Tasks.query.filter_by(id=request.form['task_id'],
                                  project_id=request.form['project_id']).first()
    if check is None:
        return jsonify({
            'result': True
        })
    return jsonify({
        'result': False
    })


@app.route('/update_task', methods=['POST'])
@login_required
def update_task():
    task = Tasks.query.filter_by(id=request.form['task_id'],
                                 project_id=request.form['project_id']).first()
    if task is None:
        return jsonify({
            'result': False
        })

    task.name = str(request.form['new_name']).strip()
    task.deadline = request.form['deadline']
    db.session.add(task)
    db.session.commit()

    check = Tasks.query.filter_by(id=request.form['task_id'],
                                  project_id=request.form['project_id']).first()
    if check.name != str(request.form['new_name']).strip() and \
                                    check.deadline != request.form['deadline']:

        return jsonify({
            'result': False
        })

    return jsonify({
        'result': True
    })


@app.route('/task_done', methods=['POST'])
@login_required
def task_done():
    status = IN_PROGRESS
    if request.form['status'] == 'true':
        status = COMPLETE

    task = Tasks.query.filter_by(id=request.form['task_id'],
                                 project_id=request.form['project_id']).first()
    task.status = status
    db.session.add(task)
    db.session.commit()

    check = Tasks.query.filter_by(id=request.form['task_id'],
                                 project_id=request.form['project_id']).first()
    if check.status == status:
        return jsonify({
            'result': True
        })

    return jsonify({
        'result': False
    })


#SQL-queries
@app.route('/queries/<query>', methods=['GET', 'POST'])
@login_required
def queries(query=None):
    response = ''
    query_title = ''
    query_number = 0

    if query == 'query_1':
        response = query_1()
        query_title = 'Get all statuses, not repeating, alphabetically ordered'
        query_number = 1

    if query == 'query_2':
        response = query_2()
        query_title = 'Get the count of all tasks in each project, order by ' \
                      'tasks count descending'
        query_number = 2

    return render_template('queries.html',
                           title='Queries',
                           queries=response,
                           query_title=query_title,
                           query_number = query_number)


# 1.get all statuses, not repeating, alphabetically ordered
def query_1():
    query = Tasks.query.group_by(Tasks.status).all()
    return query


# 2.get the count of all tasks in each project, order by tasks count descending
def query_2():
    query = db.session.query(Tasks.project_id, func.count(Tasks.project_id)).\
                       group_by(Tasks.project_id).all()
    query_list = sorted(query, key=lambda query: query[1], reverse=True)
    query_result = []
    for elem in query_list:
        sub_query = Tasks.query.filter_by(project_id=elem[0]).all()
        query_result.append(sub_query)
    return query_result


# 3.get the count of all tasks in each project, order by projects names
def query_3():
    query = Tasks.query.all()
    return query


# 4.get the tasks for all projects having the name beginning with “N” letter
def query_4():
    query = ''
    return query


# 5.get the list of all projects containing the ‘a’ letter in the middle of the name,
# and show the tasks count near each project.
# Mention that there can exist projects without tasks and tasks with project_id=NULL
def query_5():
    query = ''
    return query


# 6.get the list of tasks with duplicate names. Order alphabetically
def query_6():
    query = ''
    return query


# 7.get the list of tasks having several exact matches of both name and status,
# from the project ‘Garage’. Order by matches count
def query_7():
    query = ''
    return query


# 8.get the list of project names having more than 10 tasks in status ‘completed’.
# Order by project_id
def query_8():
    query = ''
    return query
