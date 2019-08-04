from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets.html5 import NumberInput


class LoadForm(FlaskForm):
    model = SubmitField('Model')


class DatasetForm(FlaskForm):
    dataset = SelectField('Datasets')
    preprocessing =  SelectField('Preprocessing methods')
    sample = IntegerField('Sample size',
                          widget=NumberInput(min=-1),
                          validators=[DataRequired(), NumberRange(-1)])
    division = IntegerField('Test set size',
                            widget=NumberInput(min=5, max=95),
                            validators=[DataRequired(), NumberRange(5, 95)])
    kfolds = IntegerField('Cross-validation folds',
                          widget=NumberInput(min=1, max=20),
                          validators=[DataRequired(), NumberRange(1, 20)])
    submit = SubmitField('Submit')
