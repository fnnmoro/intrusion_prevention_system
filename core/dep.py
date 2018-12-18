from threading import Thread, Event
from flask import Blueprint, render_template, request, session, redirect, url_for
import realtime
import database
from model.mitigation import Mitigator

thread = Thread()
thread_stop_event = Event()

bp = Blueprint('dep', __name__, url_prefix='/dep')

@bp.route('/detect', methods=['GET', 'POST'])
def detect():
    global thread
    num_anomalous_flows = 0

    if not thread.isAlive():
        thread = realtime.WorkerThread(thread_stop_event,
                                       [int(request.form['model'])],
                                       session['choice_features'],
                                       session['dataset_type'])
        thread.start()
    else:
        num_anomalous_flows = database.get_num_anomalous_flows()

    return render_template('dep/detect.html',
                           num_anomalous_flows=num_anomalous_flows)

@bp.route('/mitigate')
def mitigate():
    blacklist = database.get_blacklist()

    if not blacklist:
        return redirect(url_for('dep.detect'))

    text_info = ['attacker', 'target', 'anomalous flows', 'time']

    return render_template('dep/mitigate.html',
                           text_info=text_info,
                           blacklist=blacklist)

@bp.route('/false_positive', methods=['GET', 'POST'])
def false_positive():
    if request.method == 'POST':
        database.delete_false_positive(request.form['false_positive'])

        mitigation = Mitigator()
        mitigation.delete_rule(request.form['false_positive'])

    return redirect(url_for('dep.mitigate'))