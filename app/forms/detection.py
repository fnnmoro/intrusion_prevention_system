from flask_wtf import FlaskForm
from wtforms import SubmitField


class RealtimeForm(FlaskForm):
    stop = SubmitField('Stop detection')
