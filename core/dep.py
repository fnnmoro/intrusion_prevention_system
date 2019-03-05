from threading import Thread, Event
from flask import (request, redirect, render_template,
                   url_for, session, Blueprint)
from core import socketio
from model import database
from realtime import WorkerThread
from model.mitigation import Mitigator

thread = Thread()
event = Event()

bp = Blueprint('dep', __name__, url_prefix='/dep')


@bp.route('/detect', methods=['GET', 'POST'])
def detect():
    global thread
    anomalous_flows = 0

    if not thread.isAlive():
        thread = WorkerThread(request.form['clf'], event, session['obj_date'])
        thread.start()
    else:
        anomalous_flows = database.sum_anomalous_flows()

    return render_template('dep/detect.html',
                           anomalous_flows=anomalous_flows)


@bp.route('/mitigate')
def mitigate():
    blacklist = database.select_blacklist()

    if not blacklist:
        return redirect(url_for('dep.detect'))

    return render_template('dep/mitigate.html',
                           text=['attacker', 'target', 'time',
                                 'protocol', 'anomalous flows'],
                           blacklist=blacklist)


@bp.route('/false_positive', methods=['GET', 'POST'])
def false_positive():
    if request.method == 'POST':
        database.delete_false_positive(request.form['false_positive'])

        mtg = Mitigator()
        mtg.delete_rule(request.form['false_positive'])

    return redirect(url_for('dep.mitigate'))
