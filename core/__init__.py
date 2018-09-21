from flask import Flask

app = Flask(__name__)

# avoid circular import
import train, dep
from core import home

app.register_blueprint(train.bp)
app.register_blueprint(dep.bp)



