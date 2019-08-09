from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget, Input
from wtforms.widgets.html5 import NumberInput


class LoadForm(FlaskForm):
    model = SubmitField('Model')


class DatasetForm(FlaskForm):
    dataset = SelectField('Datasets')
    sample = IntegerField('Sample size',
                          widget=NumberInput(min=-1),
                          validators=[DataRequired(), NumberRange(-1)])
    split = IntegerField('Split size',
                            widget=NumberInput(min=5, max=95),
                            validators=[DataRequired(), NumberRange(5, 95)])
    kfolds = IntegerField('Cross-validation folds',
                          widget=NumberInput(min=1, max=20),
                          validators=[DataRequired(), NumberRange(1, 20)])
    submit = SubmitField('Submit')


class ClassifierForm(FlaskForm):
    classifiers = SelectMultipleField('Machine learning classifiers',
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput(),
                                      validators=[DataRequired()])
    preprocessing = SelectField('Preprocessing methods', coerce=int)
    features = SelectMultipleField('IP flows fetures',
                                   widget=ListWidget(prefix_label=False),
                                   option_widget=CheckboxInput(),
                                   validators=[DataRequired()])
    submit = SubmitField('Submit')
