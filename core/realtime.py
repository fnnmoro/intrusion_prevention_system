import time
from model import gatherer, tools
from model.preprocessing import Formatter, Modifier
from model.mitigation import Mitigator
from threading import Thread
from core import socketio
import database
from core import nfcapd_path, csv_path
import pickle


class WorkerThread(Thread):
    def __init__(self, event, model, choice_features, dataset_type):
        super().__init__()
        self.thread_stop_event = event
        self.model = model
        self.choice_features = choice_features
        self.dataset_type = dataset_type
        self.dt = pickle.load(open('../objects/dt', 'rb'))
        self.ex = pickle.load(open('../objects/ex', 'rb'))

    def model_execution(self):
        print('thread execution')

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

                    tools.clean_tmp_files(nfcapd_path, csv_path, True)

                    ft = Formatter(flows)
                    header, flows = ft.format_flows()

                    md = Modifier(flows, header)
                    header, flows = md.modify_flows(100, self.dataset_type)

                    header_features, features = self.ex.extract_features(
                        header, flows, self.choice_features)

                    pred, test_date, test_dur = self.dt.execute_classifiers(
                        features, 0)

                    anomalous_flows = self.dt.find_anomalies(flows, pred)

                    if anomalous_flows:
                        database.tmp_flows(anomalous_flows)

                        blacklist = database.get_anomalous_flows()

                        mitigation = Mitigator(blacklist)
                        mitigation.insert_rule()

                    socketio.emit('mytest',
                                  {'total_anomalies':
                                    database.get_num_anomalous_flows()},
                                  namespace='/test')

                    database.delete_tmp_flows()

                time.sleep(2)
        finally:
            process.kill()

    def run(self):
        self.model_execution()

    """def join(self, timeout=None):
        self.thread_stop_event.set()
        super(WorkerThread, self).join(timeout)"""


