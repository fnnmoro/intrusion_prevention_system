import time
import pickle
from flask import Blueprint, request, render_template, g
from model import gatherer
from model import tools
from view import export_flows
from model.preprocessing import Formatter, Extractor, Modifier

bp = Blueprint('dep', __name__, url_prefix='/dep')

@bp.route('/detect', methods=('GET', 'POST'))
def detect():
    if request.method == 'POST':
        nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
        csv_path = "/home/flmoro/research_project/dataset/csv/"

        dt = pickle.load(open('detector', 'rb'))
        forms = pickle.load(open('forms', 'rb'))

        _ = dt.choose_classifiers([int(request.form['algorithm'])])

        """process = gatherer.nfcapd_collector(nfcapd_path, 60)

        time.sleep(5)
        try:
            while True:
                path, files = tools.directory_content(nfcapd_path)

                skip = gatherer.convert_nfcapd_csv(path, files, csv_path, True)

                if skip == 0:
                    path, files = tools.directory_content(csv_path + "tmp_flows/", True)

                    flows, file_name = gatherer.open_csv(path, files, -1, True)

                    tools.clean_files(True)

                    ft = Formatter(flows)
                    header, flows = ft.format_flows()

                    md = Modifier(flows, header)
                    header, flows = md.modify_flows(False, True)
                    
                    ex = Extractor(flows)
                    features = ex.extract_features(forms[0])
                    features = ex.preprocessing_features(features, forms[1])

                    pred = dt.execute_classifiers(test_features=features,
                                                  execute_model=True)[0]
     
                    export_flows(flows, csv_path + "flows/", file_name, header)

                time.sleep(10)
        finally:
            process.kill()"""

    return render_template('dep/detect.html')