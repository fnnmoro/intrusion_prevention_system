from app import db


class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)

    def __repr__(self):
        return f'<Feature {self.name}>'

features = db.Table('features',
                    db.Column('feature_id', db.Integer,
                              db.ForeignKey('feature.id'), primary_key=True),
                    db.Column('model_id', db.Integer,
                              db.ForeignKey('model.id'), primary_key=True))
