from app import app, db, socketio
from app.core import tools
from app.models import (Classifier, Dataset, Feature,
                        Model, Preprocessing, Result)
from app.paths import paths


@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db, 'socketio': socketio,
            'Classifier': Classifier, 'Dataset': Dataset, 'Feature': Feature,
            'Model': Model, 'Preprocessing': Preprocessing, 'Result': Result}


if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:
        #db.delete_blacklist()
        tools.clean_files(paths['nfcapd'], '*')
