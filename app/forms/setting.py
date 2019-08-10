from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget, Input
from wtforms.widgets.html5 import NumberInput

from app.core.tools import get_content
from app.models.classifier import Classifier
from app.models.preprocessing import Preprocessing
from app.models.feature import Feature
from app.paths import paths


class LoadForm(FlaskForm):
    model = SubmitField('Model')


class DatasetForm(FlaskForm):
    dataset = SelectField('Datasets', choices=[])
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

    def dataset_choices(self):
        datasets = get_content(f'{paths["csv"]}datasets/')[1]
        for ds in datasets:
            self.dataset.choices.append([ds, ' '.join(ds.split('.csv')[0]
                                                        .split('_'))])


class ClassifierForm(FlaskForm):
    classifiers = SelectMultipleField('Machine learning classifiers',
                                      coerce=int,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput(),
                                      validators=[DataRequired()],
                                      choices=[
                                          [clf.id, clf.name]
                                          for clf in Classifier.query.all()])
    preprocessing = SelectField('Preprocessing methods',
                                coerce=int,
                                choices=[
                                    [method.id, method.name]
                                    for method in Preprocessing.query.all()])
    features = SelectMultipleField('IP flows fetures',
                                   coerce=int,
                                   widget=ListWidget(prefix_label=False),
                                   option_widget=CheckboxInput(),
                                   validators=[DataRequired()],
                                   choices=[[feat.id, feat.name]
                                            for feat in Feature.query.all()])
    submit = SubmitField('Submit')
