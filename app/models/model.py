from datetime import datetime

from app import db
from app.models.feature import features


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(100), index=True, nullable=False)
    datetime = db.Column(db.DateTime, index=True, nullable=False)
    dataset_id = db.Column(db.Integer,
                           db.ForeignKey('dataset.id'),
                           nullable=False)
    classifier_id = db.Column(db.Integer,
                              db.ForeignKey('classifier.id'),
                              nullable=False)
    preprocessing_id = db.Column(db.Integer,
                                 db.ForeignKey('preprocessing.id'),
                                 nullable=False)
    features = db.relationship('Feature',
                               secondary=features,
                               lazy='subquery',
                               backref=db.backref('models', lazy=True))
    result = db.relationship('Result', backref='model',
                             lazy=True, uselist=False)

    def __repr__(self):
        return f'<Model {self.id}>'
