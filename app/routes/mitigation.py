from flask import (Blueprint, redirect, request,
                   render_template, session, url_for)

from app import database as db
from app.core.mitigation import Mitigator


bp = Blueprint('mitigation', __name__)

@bp.route('/')
def blacklist():
    blacklist = db.select_blacklist()

    if not blacklist:
        return redirect(url_for('detection.realtime'))

    return render_template('mitigation/blacklist.html',
                           text=['attacker', 'target', 'time',
                                 'protocol', 'anomalous flows'],
                           blacklist=blacklist)


@bp.route('/remove_anomaly', methods=['GET', 'POST'])
def remove_anomaly():
    if request.method == 'POST':
        db.delete_false_positive(request.form['false_anomaly'])

        mtg = Mitigator()
        mtg.delete_flow_rule(request.form['false_anomaly'])

    return redirect(url_for('mitigation.blacklist'))
