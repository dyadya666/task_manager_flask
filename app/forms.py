from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, validators


class LoginForm(FlaskForm):
    openid = StringField('openid',
                         [validators.required('Field is required!'),
                          validators.length(max=50),
                          validators.regexp('^[^0-9]', message='Name must begin with the letter.')])


class GameForm(FlaskForm):
    try_to_guess = IntegerField(
                    'try_to_guess',
                    [validators.required('You should try)'),
                     validators.length(max=3)])