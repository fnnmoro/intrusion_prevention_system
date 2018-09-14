from flask import Flask, render_template
import train

app = Flask(__name__)

app.register_blueprint(train.bp)

@app.route('/home')
def home():
    return render_template('home.html')
