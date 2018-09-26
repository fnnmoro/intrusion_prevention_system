import os
import sqlite3
from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flows.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from core import db
    from core import train, dep
    db.init_db(app)

    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('home.html')

    app.register_blueprint(train.bp)
    app.register_blueprint(dep.bp)

    return app
