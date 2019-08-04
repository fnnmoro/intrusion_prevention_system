from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField


class LoadForm(FlaskForm):
    model = SubmitField('Model')
