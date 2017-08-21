import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_openid import OpenID

from config import basedir


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

log_manager = LoginManager()
log_manager.init_app(app)
log_manager.login_view = 'login'

open_id = OpenID(app, os.path.join(basedir, 'tmp'))


from app import views, models