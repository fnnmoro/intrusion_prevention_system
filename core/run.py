from core import app
from core import socketio
from core.model.database import delete_blacklist
from core.model.tools import clean_files
from path import folders

if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:
        delete_blacklist()
        clean_files(folders['nfcapd'], '*')
