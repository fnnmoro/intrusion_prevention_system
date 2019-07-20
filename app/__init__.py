import os

from flask import Flask, render_template
from flask_socketio import SocketIO

from config import Config


app = Flask(__name__)#, instance_relative_config=True)
app.config.from_object(Config)
app.jinja_env.add_extension('jinja2.ext.do')

socketio = SocketIO(app)

from app.path import paths
from app.core import tools
from app.routes import creation, root, train


for path in paths.values():
    tools.make_dir(path)

app.register_blueprint(root.bp)
app.register_blueprint(creation.bp, url_prefix='/creation')
app.register_blueprint(train.bp, url_prefix='/train')
#app.register_blueprint(dep.bp)
