from app import app, db, socketio
from app.core import util
from app.models import (Classifier, Dataset, Feature,
                        Intrusion, Model, Preprocessing,
                        Result)


@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db, 'socketio': socketio,
            'Classifier': Classifier, 'Dataset': Dataset,
            'Feature': Feature, 'Intrusion': Intrusion,
            'Model': Model, 'Preprocessing': Preprocessing,
            'Result': Result}


if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:
        for itr in Intrusion.query.all():
            db.session.delete(itr)
        db.session.commit()

        util.clean_directory(util.paths['nfcapd'], '*')
