import os
from flask import Flask, redirect, render_template, url_for
from flask_socketio import SocketIO
from path import paths
from model.tools import make_dir


for path in paths.values():
    make_dir(path)

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(SECRET_KEY='h7cn#403mks-',
                        DATABASE=os.path.join(app.instance_path,
                                              'network_data.db'),
                        DEBUG=True)
app.config.from_pyfile('config.py', silent=True)
app.jinja_env.add_extension('jinja2.ext.do')

socketio = SocketIO(app)

from core import train, dep
from model.database import delete_blacklist
from model.tools import clean_files

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/clean')
def clean():
    delete_blacklist()
    clean_files([paths['nfcapd']], ['*'])

    return redirect(url_for('home'))


app.register_blueprint(train.bp)
app.register_blueprint(dep.bp)
