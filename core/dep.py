import time
import pickle
from flask import Blueprint, request, render_template, g
from model import gatherer
from model import tools
from view import export_flows
from model.preprocessing import Formatter, Extractor, Modifier

bp = Blueprint('dep', __name__, url_prefix='/dep')

@bp.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
        csv_path = "/home/flmoro/research_project/dataset/csv/"

        dt = pickle.load(open('detector', 'rb'))
        forms = pickle.load(open('forms', 'rb'))

        _ = dt.choose_classifiers([int(request.form['algorithm'])])

    return render_template('dep/detect.html')