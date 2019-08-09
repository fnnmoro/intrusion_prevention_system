from app import db


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_date = db.Column(db.DateTime, nullable=False)
    test_date = db.Column(db.DateTime, nullable=False)
    train_duration = db.Column(db.Float, nullable=False)
    test_duration = db.Column(db.Float, nullable=False)
    hyperparameters = db.Column(db.Text, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    true_negative = db.Column(db.Integer, nullable=False)
    false_positive = db.Column(db.Integer, nullable=False)
    false_negative = db.Column(db.Integer, nullable=False)
    true_positive = db.Column(db.Integer, nullable=False)
    model_id = db.Column(db.Integer,
                         db.ForeignKey('model.id'),
                         nullable=False)

    def __repr__(self):
        return f'<Result {self.train_date}>'
