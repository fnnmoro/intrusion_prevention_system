import os
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO
from model import tools


dataset_path = "/home/flmoro/bsi16/research_project/codes/dataset/"
pcap_path = "/home/flmoro/bsi16/research_project/codes/dataset/pcap/"
nfcapd_path = "/home/flmoro/bsi16/research_project/codes/dataset/nfcapd/"
csv_path = "/home/flmoro/bsi16/research_project/codes/dataset/csv/"
log_path = "/home/flmoro/bsi16/research_project/codes/log/"
obj_path = "/home/flmoro/bsi16/research_project/codes/anomaly_detector/objects/"

tools.check_path_exist(pcap_path, nfcapd_path, csv_path, log_path)

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(SECRET_KEY='h7cn#403mks-',
                        DATABASE=os.path.join(app.instance_path,
                                              'network_data.db'),
                        DEBUG=True)

app.config.from_pyfile('config.py', silent=True)

socketio = SocketIO(app)

import database
from core import train, dep
from core.model.tools import clean_files

database.create_database()

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/clean')
def clean():
    clean_files(nfcapd_path, obj_path)

    return redirect(url_for('home'))

app.register_blueprint(train.bp)
app.register_blueprint(dep.bp)



