from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.widgets.html5 import NumberInput



class ContentForm(FlaskForm):
    files = SelectMultipleField('Files',
                                widget=ListWidget(prefix_label=False),
                                option_widget=CheckboxInput(),
                                validators=[DataRequired()],
                                choices=[])
    submit = SubmitField('Submit')

    def files_choices(self, files):
        for file in files:
            self.files.choices.append([file, file])


class SplitPcapForm(FlaskForm):
    split = IntegerField('Split size',
                         widget=NumberInput(min=50, max=1000),
                         validators=[DataRequired(), NumberRange(50, 1000)])
    submit = SubmitField('Submit')


class ConvertPcapNfcapdForm(FlaskForm):
    window = IntegerField('Time window',
                          widget=NumberInput(min=5, max=300),
                          validators=[DataRequired(), NumberRange(5, 300)])
    submit = SubmitField('Submit')


class ConvertNfcapdCsvForm(FlaskForm):
    name = StringField('File name',
                       validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Submit')


class PreprocessingFlowsForm(FlaskForm):
    sample = IntegerField('Sample size',
                          widget=NumberInput(min=-1),
                          validators=[InputRequired(), NumberRange(-1)])
    threshold = IntegerField('Aggregation threshold',
                             widget=NumberInput(min=10, max=1000),
                             validators=[DataRequired(),
                                         NumberRange(10, 1000)])
    label = IntegerField('Flows label',
                         widget=NumberInput(min=0, max=10),
                         validators=[InputRequired(), NumberRange(0, 10)])
    submit = SubmitField('Submit')


class MergingFlowsForm(FlaskForm):
    name = StringField('File name',
                       validators=[DataRequired(), Length(max=50)])
    window = StringField('Time window defined',
                         validators=[DataRequired(), Length(max=3)])
    threshold = StringField('Threshold defined',
                            validators=[DataRequired(), Length(max=4)])

    submit = SubmitField('Submit')
