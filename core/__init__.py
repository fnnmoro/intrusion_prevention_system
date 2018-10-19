import os
import sqlite3
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='h7cn#403mks-',
    DATABASE=os.path.join(app.instance_path, 'flows.sqlite'),
    DEBUG=True
)

app.config.from_pyfile('config.py', silent=True)

socketio = SocketIO(app)

from core import database
from core import train, dep

database.init_db(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

app.register_blueprint(train.bp)
app.register_blueprint(dep.bp)



