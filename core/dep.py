import pickle
from threading import Thread, Event
from flask import Blueprint, render_template, request, session
import realtime
import database

thread = Thread()
thread_stop_event = Event()

bp = Blueprint('dep', __name__, url_prefix='/dep')

@bp.route('/detect', methods=['GET', 'POST'])
def detect():
    global thread

    dt = pickle.load(open('../objects/dt', 'rb'))
    ex = pickle.load(open('../objects/ex', 'rb'))

    if not thread.isAlive():
        thread = realtime.WorkerThread(dt, ex, thread_stop_event,
                                       [int(request.form['model'])],
                                       session['choice_features'],
                                       session['preprocessing'],
                                       session['dataset_type'])
        thread.start()

    return render_template('dep/detect.html')

@bp.route('/blacklist')
def blacklist():
    text_info = ['target', 'anomalous flows']

    anomalous_flows = database.get_anomalous_flows()

    return render_template('dep/blacklist.html',
                           text_info=text_info,
                           anomalous_flows=anomalous_flows)

@bp.route('/mitigation', methods=['GET', 'POST'])
def mitigation():
    return render_template('dep/mitigation.html')
