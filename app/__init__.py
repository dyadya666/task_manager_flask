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

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('tmp/task_manager.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO),
    file_handler.setLevel(logging.INFO),
    app.logger.addHandler(file_handler),
    app.logger.info('task_manager')



from app import views, models
