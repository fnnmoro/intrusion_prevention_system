from app import db


class Classifier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    models = db.relationship('Model', backref='classifier', lazy=True)

    def __repr__(self):
        return f'<Classifier {self.id}: {self.name}>'


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(50), index=True, nullable=False)
    window = db.Column(db.Integer, nullable=False)
    aggregation = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    split = db.Column(db.Integer, nullable=False)
    kfolds = db.Column(db.Integer, nullable=False)
    models = db.relationship('Model', backref='dataset', lazy=True)

    def __repr__(self):
        return f'<Dataset {self.id}: {self.file}>'


class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)

    def __repr__(self):
        return f'<Feature {self.id}: {self.name}>'


features = db.Table('features',
                    db.Column('feature_id', db.Integer,
                              db.ForeignKey('feature.id'), primary_key=True),
                    db.Column('model_id', db.Integer,
                              db.ForeignKey('model.id'), primary_key=True))


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
    features = db.relationship('Feature', secondary=features,
                               lazy='subquery',
                               backref=db.backref('models', lazy=True))
    result = db.relationship('Result', backref='model',
                             lazy=True, cascade='all, delete',
                             uselist=False)

    def __repr__(self):
        return f'<Model {self.id}: {self.file}>'


class Preprocessing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    models = db.relationship('Model', backref='preprocessing', lazy=True)

    def __repr__(self):
        return f'<Preprocessing {self.id}: {self.name}>'


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_date = db.Column(db.DateTime, nullable=False)
    test_date = db.Column(db.DateTime, nullable=False)
    train_duration = db.Column(db.Float, nullable=False)
    test_duration = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    true_negative = db.Column(db.Integer, nullable=False)
    false_positive = db.Column(db.Integer, nullable=False)
    false_negative = db.Column(db.Integer, nullable=False)
    true_positive = db.Column(db.Integer, nullable=False)
    hyperparameters = db.Column(db.Text, nullable=False)
    model_id = db.Column(db.Integer,
                         db.ForeignKey('model.id'),
                         nullable=False)

    def __repr__(self):
        return f'<Result {self.id}: {self.train_date}>'


class Intrusion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, index=True, nullable=False)
    end_time = db.Column(db.DateTime, index=True, nullable=False)
    source_address = db.Column(db.String(39), nullable=False)
    destination_address = db.Column(db.String(39), nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    flags = db.Column(db.String(100), nullable=False)
    source_port = db.Column(db.Text, nullable=False)
    destination_port = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    packets = db.Column(db.Integer, nullable=False)
    bytes = db.Column(db.Integer, nullable=False)
    bytes_per_second = db.Column(db.Integer, nullable=False)
    bytes_per_packets = db.Column(db.Integer, nullable=False)
    packtes_per_second = db.Column(db.Integer, nullable=False)
    number_source_port = db.Column(db.Integer, nullable=False)
    number_destination_port = db.Column(db.Integer, nullable=False)
    flows = db.Column(db.Integer, nullable=False)
    rule = db.Column(db.String(10), nullable=False)
    model_id = db.Column(db.Integer,
                         db.ForeignKey('model.id'),
                         nullable=False)

    def __repr__(self):
        return (f'<Intrusion {self.id}: '
                f'{self.source_address} -> {self.destination_address} '
                f'{self.rule}>')
