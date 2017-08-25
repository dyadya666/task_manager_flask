from flask import render_template, redirect, url_for, request, jsonify, g
from flask_login import login_required

from app import app, db, open_id, log_manager
from .models import Users, Projects, Tasks


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
