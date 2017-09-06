from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, redirect, url_for, request, jsonify, g

from app import app, db, open_id, log_manager
from .forms import LoginForm
from .models import Users, Projects, Tasks, COMPLETE, IN_PROGRESS


@log_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


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


# API for Projects
@app.route('/create_project', methods=['POST'])
# @login_required
def create_project(name=None, user_id=None, test=None):
    if name is None and user_id is None:
        name = request.form['name']
        user_id = g.user.id

    new_project = Projects(name=name, user_id=user_id)
    db.session.add(new_project)
    db.session.commit()

    check = Projects.query.filter_by(user_id=user_id,
                                    name=name).first()

    if test == True:
        return check

    if check is None:
        return jsonify({
            'result': False
        })
    return jsonify({
        'result': True
    })


@app.route('/delete_project', methods=['POST'])
# @login_required
def delete_project(id=None, user_id=None, test=None):
    if id is None and user_id is None:
        id = request.form['project_id']
        user_id = g.user.id

    project = Projects.query.filter_by(id=id,
                                       user_id=user_id).first()
    db.session.delete(project)
    db.session.commit()

    try:
        Projects.query.filter_by(id=request.form['id'],
                                 user_id=g.user.id).first()

        return jsonify({
            'result': False
        })
    except:
        if test is True:
            return True

        return jsonify({
            'result': True
        })


@app.route('/update_project', methods=['POST'])
# @login_required
def update_project(id=None, user_id=None, new_name=None, test=None):
    if test is None:
        id  = request.form['project_id']
        user_id = g.user.id
        new_name = request.form['new_name']

    project = Projects.query.filter_by(id=id, user_id=user_id).first()
    project.name = new_name
    db.session.add(project)
    db.session.commit()

    check = Projects.query.filter_by(id=id, user_id=user_id).first()
    if check.name == new_name:
        if test is True:
            return True

        return jsonify({
            'result': True
        })

    return jsonify({
        'result': False
    })


@app.route('/change_priority', methods=['POST'])
# @login_required
def change_priority(id_task_to_move=None,
                    project_id=None,
                    up_down=None,
                    test=None):
    if id_task_to_move is None \
            and project_id is None \
            and up_down is None:
        id_task_to_move = request.form['task_id']
        project_id = request.form['project_id']
        up_down = request.form['up_down']

    task_to_move = Tasks.query.filter_by(id=id_task_to_move,
                                         project_id=project_id).first()
    list_of_priority = get_list_of_priorities(project_id)

    if up_down == 'up':
        if list_of_priority.index(task_to_move.priority) - 1 < 0:
            if test is True:
                return True

            return jsonify({
                'result': True
            })

        priority_of_previous_task = \
                    list_of_priority[
                        list_of_priority.index(task_to_move.priority)
                                    ] - 1

        previous_task = Tasks.query.filter_by(
                                    project_id=project_id,
                                    priority=priority_of_previous_task).first()
        previous_task.priority = task_to_move.priority
        task_to_move.priority = priority_of_previous_task
        db.session.add(task_to_move)
        db.session.add(previous_task)
        try:
            db.session.commit()

            if test is True:
                return True

            return jsonify({
                'result': True
            })
        except:
            return jsonify({
                'result': False
            })

    if up_down == 'down':
        try:
            priority_of_next_task = \
                    list_of_priority[
                        list_of_priority.index(task_to_move.priority)
                        + 1]
        except IndexError:
            db.session.commit()

            if test is True:
                return True

            return jsonify({
                'result': True
            })

        next_task = Tasks.query.filter_by(
                        project_id=project_id,
                        priority=priority_of_next_task).first()
        next_task.priority = task_to_move.priority
        task_to_move.priority = priority_of_next_task
        db.session.add(task_to_move)
        db.session.add(next_task)
        try:
            db.session.commit()

            if test is True:
                return True

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
# @login_required
def create_task(new_task_name=None, project_id=None, test=None):
    if new_task_name is None and project_id is None:
        new_task_name = str(request.form['new_name']).strip()
        project_id = request.form['project_id']

    new_task = Tasks(name=new_task_name, project_id=project_id)
    new_task.priority = Tasks.query.filter_by(project_id=project_id).count()
    db.session.add(new_task)
    db.session.commit()

    check = Tasks.query.filter_by(name=new_task_name,
                                  project_id=project_id).first()

    if check is None:
        return jsonify({
            'result': False
        })

    if test is True:
        return True

    return jsonify({
        'result': True
    })


@app.route('/delete_task', methods=['POST'])
# @login_required
def delete_task(id=None, project_id=None, test=None):
    if id is None and project_id is None:
        id = request.form['task_id']
        project_id = request.form['project_id']

    task = Tasks.query.filter_by(id=id, project_id=project_id).first()
    db.session.delete(task)
    db.session.commit()

    check = Tasks.query.filter_by(id=id, project_id=project_id).first()
    if check is None:
        if test is True:
            return True

        return jsonify({
            'result': True
        })
    return jsonify({
        'result': False
    })


@app.route('/update_task', methods=['POST'])
# @login_required
def update_task(id=None,
                project_id=None,
                new_name=None,
                deadline=None,
                test=None):
    if id is None \
            and project_id is None \
            and new_name is None \
            and deadline is None:
        id = request.form['task_id']
        project_id = request.form['project_id']
        new_name = str(request.form['new_name']).strip()
        deadline = request.form['deadline']

    task = Tasks.query.filter_by(id=id, project_id=project_id).first()
    if task is None:
        return jsonify({
            'result': False
        })

    task.name = new_name
    task.deadline = deadline
    db.session.add(task)
    db.session.commit()

    check = Tasks.query.filter_by(id=id, project_id=project_id).first()

    if check.name != new_name and check.deadline != deadline:
        return jsonify({
            'result': False
        })

    if test is True:
        return True

    return jsonify({
        'result': True
    })


@app.route('/task_done', methods=['POST'])
# @login_required
def task_done(task_id=None, project_id=None, status_checkbox=None, test=None):
    if task_id is None and project_id is None and status_checkbox is None:
        task_id = request.form['task_id']
        project_id = request.form['project_id']
        status_checkbox = request.form['status']

    status = IN_PROGRESS
    if status_checkbox == 'true':
        status = COMPLETE

    task = Tasks.query.filter_by(id=task_id, project_id=project_id).first()
    task.status = status
    db.session.add(task)
    db.session.commit()

    check = Tasks.query.filter_by(id=task_id, project_id=project_id).first()
    if check.status == status:
        if test is True:
            return True

        return jsonify({
            'result': True
        })

    return jsonify({
        'result': False
    })
