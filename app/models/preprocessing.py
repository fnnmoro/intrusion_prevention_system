from app import db


class Preprocessing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    models = db.relationship('Model', backref='preprocessing', lazy=True)

    def __repr__(self):
        return f'<Preprocessing {self.name}>'
