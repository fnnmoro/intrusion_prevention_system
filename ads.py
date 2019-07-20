from app import app, socketio
from app.core.database import delete_blacklist


if __name__ == '__main__':
    try:
        socketio.run(app)
    finally:
        delete_blacklist()
