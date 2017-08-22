from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, validators


class LoginForm(FlaskForm):
    openid = StringField('openid',
                         [validators.required('Field is required!')])
