from app import db


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(50), index=True, nullable=False)
    window = db.Column(db.Integer, nullable=False)
    aggregation = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    sample = db.Column(db.Integer, nullable=False)
    split = db.Column(db.Integer, nullable=False)
    kfolds = db.Column(db.Integer, nullable=False)
    models = db.relationship('Model', backref='dataset', lazy=True)

    def __repr__(self):
        return f'<Dataset {self.file}>'
