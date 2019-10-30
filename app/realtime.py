import ast
import logging
import pickle
import time
import threading

from sqlalchemy import func

from app import db, socketio
from app.core import gatherer, util
from app.core.mitigation import Mitigator
from app.core.preprocessing import Extractor, Formatter, Modifier
from app.models import Dataset, Intrusion


logger = logging.getLogger('realtime')


class RealtimeThread(threading.Thread):
    def __init__(self, event, model):
        super().__init__()
        self.event = event
        self.model = model
        self.detector = pickle.load(open(f'{util.paths["models"]}'
                                         f'{self.model.file}', 'rb'))
        self.mitigator = Mitigator()

    def execution(self):
        process = gatherer.capture_nfcapd(util.paths['nfcapd'], 60)
        dataset = Dataset.query.get(self.model.dataset_id)
        logger.info(f'process pid: {process.pid}')
        logger.info(f'dataset file: {dataset.file}')

        try:
            while not self.event.is_set():
                nfcapd_files = util.directory_content(util.paths['nfcapd'])[1]

                try:
                    if not 'current' in nfcapd_files[0]:
                        logger.info(f'nfcapd files: {nfcapd_files[:-1]}')

                        # gathering flows.
                        flows = self.gathering(nfcapd_files[:-1])

                        # cleaning remaining files
                        util.clean_directory(util.paths['nfcapd'],
                                             'nfcapd.20*')
                        util.clean_directory(f'{util.paths["csv"]}tmp/', '*')

                        if len(flows[0]) < 18:
                            raise ValueError('No matched flows')
                        logger.info(f'flow: {flows[0]}')

                        # preprocessing flows.
                        formatter = Formatter()
                        flows = formatter.format_flows(flows)
                        logger.info(f'formatted flow: {flows[0]}')

                        modifier = Modifier(2, dataset.aggregation)
                        extractor = Extractor([feature.id+7 for feature in
                                               self.model.features])

                        while flows:
                            flow, flows = modifier.aggregate(flows)
                            features, _ = extractor.extract(flow)
                            # detecting intrusions.
                            pred, _, _ = self.detector.test([features])

                            if pred[0]:
                                # mitigating intrusions.
                                self.mitigating(flow)
                    time.sleep(2)
                except IndexError:
                    time.sleep(2)
                    continue
                except ValueError as error:
                    logger.error(error)
                    util.clean_directory(util.paths['nfcapd'], 'nfcapd.20*')
                    util.clean_directory(f'{util.paths["csv"]}tmp/', '*')
                    continue
        finally:
            logger.info('thread status: false')
            process.kill()

    def gathering(self, nfcapd_files):
        gatherer.convert_nfcapd_csv(util.paths['nfcapd'], nfcapd_files,
                                    f'{util.paths["csv"]}tmp/',
                                    'realtime')
        csv_file = util.directory_content(f'{util.paths["csv"]}tmp/')[1]
        logger.info(f'csv files: {csv_file[0]}')
        _, flows = gatherer.open_csv(f'{util.paths["csv"]}tmp/', csv_file[0])

        return flows

    def mitigating(self, flow):
        intrusion = Intrusion.query.filter_by(source_address=flow[2],
                                              destination_address=flow[3],
                                              protocol=flow[4]).all()

        if not intrusion:
            logger.info(f'intrusion: {flow}')

            intrusion = Intrusion(start_time=flow[0], end_time=flow[1],
                                  source_address=flow[2],
                                  destination_address=flow[3],
                                  protocol=flow[4], flags=str(flow[5]),
                                  source_port=str(flow[6]),
                                  destination_port=str(flow[7]),
                                  duration=flow[8], packets=flow[9],
                                  bytes=flow[10], bytes_per_second=flow[11],
                                  bytes_per_packets=flow[12],
                                  packtes_per_second=flow[13],
                                  number_source_port=flow[14],
                                  number_destination_port=flow[15],
                                  flows=flow[16], rule='no rule',
                                  model_id=self.model.id)
            self.mitigator.block_attack(intrusion)

            num_intrusions = db.session.query(Intrusion).count()
            logger.info(f'number of intrusions: {num_intrusions}')
            socketio.emit('detection',
                          {'num_intrusions': num_intrusions},
                          namespace='/realtime')
        else:
            intrusion = intrusion[0]
            intrusion.end_time = flow[1]
            flags = ast.literal_eval(intrusion.flags)
            intrusion.flags = str([x+y for x, y in zip(flags, flow[5])])
            sp = ast.literal_eval(intrusion.source_port) | flow[6]
            dp = ast.literal_eval(intrusion.destination_port) | flow[7]
            intrusion.source_port = str(sp)
            intrusion.destination_port = str(dp)
            intrusion.duration = (flow[1] - intrusion.start_time).seconds
            intrusion.packets += flow[9]
            intrusion.bytes += flow[10]
            if intrusion.duration:
                bps = intrusion.bytes/intrusion.duration
                pps = intrusion.packets/intrusion.duration
            else:
                bps, pps = 0, 0
            bpp = intrusion.bytes/intrusion.packets
            intrusion.bytes_per_second = int(round(bps))
            intrusion.bytes_per_packets = int(round(bpp))
            intrusion.packtes_per_second = int(round(pps))
            intrusion.number_source_port = len(sp)
            intrusion.number_destination_port = len(dp)
            intrusion.flows += flow[16]
        db.session.add(intrusion)
        db.session.commit()

    def run(self):
        logger.info('thread status: True')
        self.execution()
