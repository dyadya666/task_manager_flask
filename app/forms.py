from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, validators


class LoginForm(FlaskForm):
    nickname = StringField('nickname',
                         [validators.required('Field is required!')])
    password = StringField('password',
                           [validators.required('Field is required!')])
