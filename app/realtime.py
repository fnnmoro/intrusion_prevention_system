import time
import pickle
from threading import Thread
from core import socketio
from path import paths
from model.gatherer import capture_nfcapd, convert_nfcapd_csv, open_csv
from model.preprocess import Formatter, Modifier
from model.mitigation import Mitigator
from model.tools import clean_files, get_content
from model import database


class WorkerThread(Thread):
    def __init__(self, clf, event, obj_name):
        super().__init__()
        self.clf = clf
        self.count = 0
        self.event = event
        self.obj = pickle.load(open(f'{paths["saves"]}{obj_name}', 'rb'))[:2]

    def preprocess(self, files):
        convert_nfcapd_csv(paths['nfcapd'], [files],
                           f'{paths["tmp"]}',
                           'execute')

        files = get_content(f'{paths["tmp"]}')[1]

        header, flows = open_csv(f'{paths["tmp"]}', files[0])

        clean_files(paths['nfcapd'], 'nfcapd.20*')
        clean_files(f'{paths["tmp"]}', '*')

        formatter = Formatter(header, flows)
        header = formatter.format_header()
        flows = formatter.format_flows()

        modifier = Modifier(flows, header)

        if self.obj[0].start_idx == 6:
            header, flows = modifier.aggregate_flows(100)
        header, flows = modifier.create_features(2)

        features, label = self.obj[0].extract_features(flows)

        return features, flows

    def mitigation(self, pred):
        if 1 in pred:
            blacklist = None
            while not blacklist:
                blacklist = database.create_blacklist()
                time.sleep(2)

            mtg = Mitigator(self.count, blacklist)
            mtg.insert_flow_rules()
            self.count += getattr(mtg, 'count')

            socketio.emit('detect',
                          {'anomalous_flows': database.sum_anomalous_flows()},
                           namespace='/dep')

        database.delete_flows()

    def execution(self):
        process = capture_nfcapd(paths['nfcapd'], 60)

        time.sleep(2)
        try:
            while not self.event.isSet():
                files = get_content(paths['nfcapd'])[1]

                try:
                    if not 'current' in files[0]:
                        features, flows = self.preprocess(files[0])

                        pred, date, dur = (self.obj[1]
                                               .execute_classifier(self.clf,
                                                                   features))

                        flows = self.obj[1].add_predictions(flows, pred)
                        database.insert_flows(flows)

                        self.mitigation(pred)
                    time.sleep(2)
                except IndexError:
                    continue
        finally:
            process.kill()

    def run(self):
        self.execution()
