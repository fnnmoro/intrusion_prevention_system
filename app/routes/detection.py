import logging
import re
import threading

from flask import (Blueprint, redirect, request,
                   render_template, session, url_for)

from app import db
from app.models import Intrusion, Model
from app.realtime import RealtimeThread


bp = Blueprint('detection', __name__)
logger = logging.getLogger('detection')
thread = None


@bp.route('/', methods=['GET', 'POST'])
def realtime():
    global thread

    if request.method == 'POST' and re.search('load', request.referrer):
        model = Model.query.get(request.form['model_pk'])
    else:
        model = Model.query.all()[-1]
    logger.info(f'model file: {model.file}')

    if not re.search('mitigation', request.referrer):
        thread = RealtimeThread(threading.Event(), model)
        thread.start()
    num_intrusions = db.session.query(Intrusion).count()

    return render_template('detection/realtime.html',
                           num_intrusions=num_intrusions)


@bp.route('/stop')
def stop():
    thread.event.set()

    return redirect(url_for('root.home'))
