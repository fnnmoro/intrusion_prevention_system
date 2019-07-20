from app import app, socketio
from app import database as db
from app.core import tools
from app.path import paths


if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:
        db.delete_blacklist()
        tools.clean_files(paths['nfcapd'], '*')
