import time
import pickle
from flask import Blueprint, render_template
from model import gatherer
from model import tools
from view import export_flows
from model.preprocessing import Formatter, Extractor, Modifier
from core.db import get_db

bp = Blueprint('dep', __name__, url_prefix='/dep')

def realtime_detection(dt, ex):
    dataset_path = "/home/flmoro/research_project/dataset/"
    pcap_path = "/home/flmoro/research_project/dataset/pcap/"
    nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
    csv_path = "/home/flmoro/research_project/dataset/csv/"

    process = gatherer.nfcapd_collector(nfcapd_path, 60)

    time.sleep(5)
    try:
        while True:
            path, files = tools.directory_content(nfcapd_path, True)

            skip = gatherer.convert_nfcapd_csv(path, files, csv_path, True)

            if skip == 0:
                path, files = tools.directory_content(csv_path
                                                      + "tmp_flows/", True)

                flows, file_name = gatherer.open_csv(path, files[0],
                                                     -1, True)

                tools.clean_files(nfcapd_path, csv_path, True)

                ft = Formatter(flows)
                header, flows = ft.format_flows()

                md = Modifier(flows, header)
                header, flows = md.modify_flows(100)

                header_features, features = ex.extract_features(
                    header, flows, list(range(10, 13)))
                labels = ex.extract_labels(flows)

                features = ex.feature_scaling(features, 2, True)

                _ = dt.choose_classifiers([0])

                pred, param, date, duration = dt.execute_classifiers(
                    0, features, 0, 0, True)

                for idx, entry in enumerate(flows):
                    entry[-1] = pred[idx]

                export_flows(flows, csv_path + "flows/",
                             file_name.split(".csv")[0] + "_w60.csv",
                             header)

            time.sleep(2)
    finally:
        process.kill()

@bp.route('/detect', methods=['GET', 'POST'])
def detect():
    db = get_db()

    db.execute(
        'INSERT INTO user (username, password) VALUES ("fernando", "pass")',
    )
    db.commit()

    user = db.execute('SELECT * FROM user WHERE username = ?', ('fernando',)).fetchone()

    print(user['username'])

    """if request.method == 'POST':
        nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
        csv_path = "/home/flmoro/research_project/dataset/csv/"

        dt = pickle.load(open('detector', 'rb'))
        ex = pickle.load(open('detector', 'rb'))
        forms = pickle.load(open('forms', 'rb'))

        _ = dt.choose_classifiers([int(request.form['algorithm'])])"""

    return render_template('dep/detect.html')