import time
import sqlite3
from model import gatherer
from model import tools
from view import export_flows
from model.preprocessing import Formatter, Extractor, Modifier
from threading import Thread
from core import socketio
from db import store_flows

class WorkerThread(Thread):
    def __init__(self, dt, ex, event, model, forms):
        super().__init__()
        self.thread_stop_event = event
        self.nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
        self.csv_path = "/home/flmoro/research_project/dataset/csv/"

        self.dt = dt
        self.ex = ex
        self.model = model
        self.choice_features = forms[0]
        self.preprocessing = forms[1]


    def model_execution(self):
        print('thread execution')
        total_anomalies = 0

        process = gatherer.nfcapd_collector(self.nfcapd_path, 60)

        _ = self.dt.choose_classifiers(self.model)

        time.sleep(2)
        try:
            while not self.thread_stop_event.isSet():
                path, files = tools.directory_content(self.nfcapd_path, True)

                skip = gatherer.convert_nfcapd_csv(path, files, self.csv_path,
                                                   True)

                if skip == 0:
                    path, files = tools.directory_content(self.csv_path
                                                          + "tmp_flows/",
                                                          True)

                    flows, file_name = gatherer.open_csv(path, files[0],
                                                         -1, True)

                    tools.clean_files(self.nfcapd_path, self.csv_path, True)

                    ft = Formatter(flows)
                    header, flows = ft.format_flows()

                    md = Modifier(flows, header)
                    header, flows = md.modify_flows(100)

                    header_features, features = self.ex.extract_features(
                        header, flows, self.choice_features)

                    features = self.ex.feature_scaling(features,
                                                       self.preprocessing, True)


                    print(self.dt.classifiers)
                    print(self.ex.preprocessing)

                    pred, param, date, duration = self.dt.execute_classifiers(
                        0, features, 0, 0, True)

                    flows, anomalies = self.dt.find_anomalies(flows, pred)

                    export_flows(flows, self.csv_path + "flows/",
                                 file_name.split(".csv")[0] + "_w60.csv",
                                 header)

                    store_flows(flows)

                    total_anomalies += anomalies

                    print('number of anomalies', total_anomalies)

                    socketio.emit('mytest', {'total_anomalies': total_anomalies},
                                  namespace='/test')

                time.sleep(2)
        finally:
            process.kill()

    def run(self):
        self.model_execution()

    """def join(self, timeout=None):
        self.thread_stop_event.set()
        super(WorkerThread, self).join(timeout)"""


