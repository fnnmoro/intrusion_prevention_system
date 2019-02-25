from core import app
from core import socketio
from core import paths
from core.model.database import delete_blacklist
from core.model.tools import clean_files


if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:
        delete_blacklist()
        clean_files([paths['nfcapd'], paths['obj']], ['*', '*'])
