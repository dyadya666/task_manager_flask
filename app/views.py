import random

from flask import render_template, redirect, url_for, request, jsonify

from app import app, db, open_id
from .forms import LoginForm
from .models import User, Score


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
@open_id.loginhandler
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=str(form.openid.data).capitalize()).first()
        if user is None:
            username = str(form.openid.data).capitalize()
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        return redirect(url_for('game', username=user.username))
    return render_template('login.html',
                           title='Log In',
                           form=form)


@app.route('/game/<username>', methods=['GET', 'POST'])
def game(username):
    form = GameForm()
    form.number_to_guess = random.randint(0, 100)
    user = User.query.filter_by(username=username).first()
    score = Score(number=form.number_to_guess,
                  user_id=user.id,
                  status='inprocess',
                  progress='')
    db.session.add(score)
    db.session.commit()
    return render_template('game.html',
                           title='Game',
                           form=form,
                           user=user)


@app.route('/write_progress', methods=['POST'])
def write_progress():
    score = Score.query.filter_by(user_id=request.form['user_id'],
                                  status='inprocess').first()
    if score is None:
        return jsonify({
            'result': False
        })
    score.progress = score.progress + ' ' + str(request.form['progress'])
    score.status = request.form['status']
    db.session.add(score)
    db.session.commit()

    return jsonify({
        'result': True
    })


@app.route('/get_stat', methods=['POST'])
def get_statistics():
    scores = Score.query.filter_by(user_id=request.form['user_id']).all()
    # import pdb; pdb.set_trace()
    list_of_usersinfo = dict()
    n = 0
    for score in scores:
        if score.status == 'inprocess':
            continue
        list_of_usersinfo[n] = str(score.number) + ', ' + \
                               score.progress + ', ' + \
                               score.status
        n += 1

    return jsonify(list_of_usersinfo)


@app.route('/end_game', methods=['POST'])
def end_game():
    score = Score.query.filter_by(user_id=request.form['user_id'],
                                  status='inprocess').first()
    score.status = 'fail'
    db.session.add(score)
    db.session.commit()
    return jsonify({
        'result': True
    })
