from threading import Thread, Event

from flask import (Blueprint, request, render_template, session)

from app import database as db
from app.realtime import WorkerThread


thread = Thread()
event = Event()

bp = Blueprint('detection', __name__)

@bp.route('/', methods=['GET', 'POST'])
def realtime():
    global thread
    anomalous_flows = 0

    if not thread.isAlive():
        thread = WorkerThread(request.form['clf'], event, session['obj_name'])
        thread.start()
    else:
        anomalous_flows = db.sum_anomalous_flows()

    return render_template('detection/realtime.html',
                           anomalous_flows=anomalous_flows)
