from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators


class LoginForm(FlaskForm):
    nickname = StringField('nickname',
                         [validators.required('Field is required!')])
    password = PasswordField('password',
                           [validators.required('Field is required!')])
