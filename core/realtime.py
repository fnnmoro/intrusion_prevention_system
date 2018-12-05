import time
from model import gatherer
from model import tools
from view import export_flows
from model.preprocessing import Formatter, Modifier
from threading import Thread
from core import socketio
from database import store_flows
from core import nfcapd_path, csv_path

class WorkerThread(Thread):
    def __init__(self, dt, ex, event, model,
                 choice_features, preprocessing, dataset_type):
        super().__init__()
        self.thread_stop_event = event
        self.dt = dt
        self.ex = ex
        self.model = model
        self.choice_features = choice_features
        self.preprocessing = preprocessing
        self.dataset_type = dataset_type

    def model_execution(self):
        print('thread execution')
        total_anomalies = 0

        process = gatherer.nfcapd_collector(nfcapd_path, 60)

        self.dt.choose_classifiers(self.model)

        time.sleep(2)
        try:
            while not self.thread_stop_event.isSet():
                path, files = tools.directory_content(nfcapd_path, True)

                skip = gatherer.convert_nfcapd_csv(path, files, csv_path, True)

                if skip == 0:
                    path, files = tools.directory_content(csv_path
                                                          + "tmp_flows/",
                                                          True)

                    flows, file_name = gatherer.open_csv(path, files[0],
                                                         -1, True)

                    tools.clean_files(nfcapd_path, csv_path, True)

                    ft = Formatter(flows)
                    header, flows = ft.format_flows()

                    md = Modifier(flows, header)
                    header, flows = md.modify_flows(100, self.dataset_type)
                    print(flows)

                    header_features, features = self.ex.extract_features(
                        header, flows, self.choice_features)

                    pred, test_date, test_dur = self.dt.execute_classifiers(
                        features, 0)

                    flows, anomalies = self.dt.find_anomalies(flows,
                                                              pred)

                    export_flows(flows,
                                 csv_path + "flows/",
                                 file_name.split(".csv")[0] + "_w60.csv",
                                 header)

                    store_flows(flows)

                    total_anomalies += anomalies

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


