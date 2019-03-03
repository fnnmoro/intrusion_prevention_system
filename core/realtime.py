import time
import pickle
from threading import Thread
from core import paths, socketio
from model.gatherer import capture_nfcapd, convert_nfcapd_csv, open_csv
from model.preprocess import Formatter, Modifier
from model.mitigation import Mitigator
from model.tools import clean_files
from model.walker import get_files
from model import database


class WorkerThread(Thread):
    def __init__(self, clf, event):
        super().__init__()
        self.clf = clf
        self.count = 0
        self.event = event
        self.ex = pickle.load(open(f'../obj/ex', 'rb'))
        self.dt = pickle.load(open(f'../obj/dt', 'rb'))

    def preprocess(self, files):
        convert_nfcapd_csv(paths['nfcapd'], [files],
                        f'{paths["csv"]}tmp_flows/',
                        'execute')

        files = get_files(f'{paths["csv"]}tmp_flows/')

        header, flows = open_csv(f'{paths["csv"]}tmp_flows/', files[0])

        clean_files([paths['nfcapd'], f'{paths["csv"]}tmp_flows/'],
                    ['nfcapd.20*', '*'])

        ft = Formatter(header, flows)
        header = ft.format_header()
        flows = ft.format_flows()

        md = Modifier(flows, header)

        if self.ex.features_idx == 6:
            header, flows = md.aggregate_flows(100)
        header, flows = md.create_features(2)

        features, label = self.ex.extract_features(flows)

        return features, flows

    def mitigation(self, pred):
        if 1 in pred:
            blacklist = None
            while not blacklist:
                blacklist = database.create_blacklist()
                time.sleep(2)

            mtg = Mitigator(self.count, blacklist)
            mtg.insert_rule()
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
                files = get_files(paths['nfcapd'])

                try:
                    if not 'current' in files[0]:
                        features, flows = self.preprocess(files[0])

                        pred, date, dur = self.dt.execute_classifier(self.clf,
                                                                     features)

                        flows = self.dt.add_predictions(flows, pred)
                        database.insert_flows(flows)

                        self.mitigation(pred)
                    time.sleep(2)
                except IndexError:
                    continue
        finally:
            process.kill()

    def run(self):
        self.execution()
