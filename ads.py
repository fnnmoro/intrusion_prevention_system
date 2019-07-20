from app import app, socketio
from app import database as db


if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:        
        db.delete_blacklist()
