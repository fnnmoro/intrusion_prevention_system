from core import app
from core import socketio
from core import nfcapd_path, obj_path
from core.model.tools import clean_files


if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:
        clean_files(nfcapd_path, obj_path)