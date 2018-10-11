import pickle
from threading import Thread, Event
from flask import Blueprint, render_template, request
import realtime

thread = Thread()
thread_stop_event = Event()

bp = Blueprint('dep', __name__, url_prefix='/dep')

@bp.route('/detect', methods=['GET', 'POST'])
def detect():
    global thread

    dt = pickle.load(open('../objects/dt', 'rb'))
    ex = pickle.load(open('../objects/ex', 'rb'))
    forms = pickle.load(open('../objects/forms', 'rb'))

    if not thread.isAlive():
        thread = realtime.WorkerThread(dt, ex, thread_stop_event,
                                       [int(request.form['model'])],
                                       forms)
        thread.start()

    return render_template('dep/detect.html')


