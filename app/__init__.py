import logging
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate

from config import Config


app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.jinja_env.add_extension('jinja2.ext.do')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S',
                    level=logging.INFO)

from app import models
from app.routes import creation, detection, mitigation, root, setting


app.register_blueprint(root.bp)
app.register_blueprint(creation.bp, url_prefix='/creation')
app.register_blueprint(detection.bp, url_prefix='/detection')
app.register_blueprint(mitigation.bp, url_prefix='/mitigation')
app.register_blueprint(setting.bp, url_prefix='/setting')
