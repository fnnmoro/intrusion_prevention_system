from app import app, db, socketio
from app.core import tools
from app.models import (Classifier, Dataset, Feature,
                        Intrusion, Model, Preprocessing,
                        Result)
from app.paths import paths


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

        tools.clean_files(paths['nfcapd'], '*')
