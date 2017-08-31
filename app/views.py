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
        return redirect(request.args.get('next') or
                        url_for('view', nickname=g.user.nickname))
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
    list_of_priority = get_list_of_priorities(request.form['project_id'])

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


def get_list_of_priorities(project_id):
    tasks = Tasks.query.filter_by(project_id=project_id).all()
    list_of_priorities = [task.priority for task in tasks]
    list_of_priorities.sort()
    return list_of_priorities


# API for Tasks
@app.route('/create_task', methods=['POST'])
@login_required
def create_task():
    new_task = Tasks(name=str(request.form['new_name']).strip(),
                     project_id=request.form['project_id'])
    new_task.priority = Tasks.query.filter_by(
                                project_id=request.form['project_id'])\
                                .count()
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
