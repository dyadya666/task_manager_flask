from flask import render_template, redirect, url_for, request, jsonify, g
from flask_login import login_user, logout_user, current_user, login_required, \
                        UserMixin

from app import app, db, open_id, log_manager
from .forms import LoginForm
from .models import Users, Projects, Tasks


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
        user = Users.query.filter_by(nickname=form.openid.data).first()

        if user is None:
            user = Users(nickname=form.openid.data)
            db.session.add(user)
            db.session.commit()

        user = get_user(id=user.id)
        login_user(user)
        return redirect(request.args.get('next') or url_for('view'))
    return render_template('login.html',
                           title='Log In',
                           form=form,
                           error=open_id.fetch_error())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/view')
@login_required
def view():
    user = g.user
    projects = Projects.query.filter_by(user_id=user.id).all()
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
