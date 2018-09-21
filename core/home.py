from flask import render_template
from core import app

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


