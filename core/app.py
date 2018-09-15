from flask import Flask, render_template
import train, dep

app = Flask(__name__)

app.register_blueprint(train.bp)
app.register_blueprint(dep.bp)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')
