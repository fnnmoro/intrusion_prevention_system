import logging

from flask import (Blueprint, redirect, request,
                   render_template, session, url_for)

from app import db
from app.core.mitigation import Mitigator
from app.models import Intrusion


bp = Blueprint('mitigation', __name__)
logger = logging.getLogger('mitigation')


@bp.route('/', methods=['GET', 'POST'])
def intrusion():
    if request.method == 'POST':
        intrusion = Intrusion.query.get(request.form['itr_pk'])
        mitigator = Mitigator()
        mitigator.remove_rule(intrusion.rule)
        logger.info(f'removed rule: {intrusion.rule}')

        db.session.delete(intrusion)
        db.session.commit()

        return redirect(url_for('mitigation.intrusion'))
    intrusions = Intrusion.query.all()
    columns = [column.key for column in Intrusion.__table__.columns]
    columns_info = columns[:7]
    columns_quant = columns[9:18]

    return render_template('mitigation/intrusion.html',
                           columns_info=columns_info,
                           columns_quant=columns_quant,
                           intrusions=intrusions)
