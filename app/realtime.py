import pickle
import time
from threading import Thread

from app import socketio
from app import database as db
from app.core import gatherer, tools
from app.core import tools
from app.core.mitigation import Mitigator
from app.core.preprocess import Formatter, Modifier
from app.paths import paths


class WorkerThread(Thread):
    def __init__(self, clf, event, obj_name):
        super().__init__()
        self.clf = clf
        self.count = 0
        self.event = event
        self.obj = pickle.load(open(f'{paths["saves"]}{obj_name}', 'rb'))[:2]

    def preprocess(self, files):
        gatherer.convert_nfcapd_csv(paths['nfcapd'], [files],
                                    f'{paths["csv"]}tmp/',
                                    'execute')

        files = tools.get_content(f'{paths["csv"]}tmp/')[1]

        header, flows = gatherer.open_csv(f'{paths["csv"]}tmp/', files[0])

        tools.clean_files(paths['nfcapd'], 'nfcapd.20*')
        tools.clean_files(f'{paths["csv"]}tmp/', '*')

        formatter = Formatter(header, flows)
        header = formatter.format_header()
        flows = formatter.format_flows()

        modifier = Modifier(flows, header)

        if self.obj[0].start_index == 6:
            header, flows = modifier.aggregate_flows(100)
        header, flows = modifier.create_features(2)

        features, label = self.obj[0].extract_features(flows)

        return features, flows

    def mitigation(self, pred):
        if 1 in pred:
            blacklist = None
            while not blacklist:
                blacklist = db.create_blacklist()
                time.sleep(2)

            mtg = Mitigator(blacklist, self.count)
            mtg.insert_flow_rules()
            self.count += getattr(mtg, 'count')

            socketio.emit('realtime',
                          {'anomalous_flows': database.sum_anomalous_flows()},
                           namespace='/detection')

        db.delete_flows()

    def execution(self):
        process = gatherer.capture_nfcapd(paths['nfcapd'], 60)

        time.sleep(2)
        try:
            while not self.event.isSet():
                files = tools.get_content(paths['nfcapd'])[1]

                try:
                    if not 'current' in files[0]:
                        features, flows = self.preprocess(files[0])

                        pred, date, dur = (self.obj[1]
                                               .execute_classifier(self.clf,
                                                                   features))

                        flows = self.obj[1].add_predictions(flows, pred)
                        db.insert_flows(flows)

                        self.mitigation(pred)
                    time.sleep(2)
                except IndexError:
                    continue
        finally:
            process.kill()

    def run(self):
        self.execution()
