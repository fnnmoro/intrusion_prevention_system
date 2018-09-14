import os
import sys
import unittest
from datetime import datetime
sys.path.append(os.path.abspath('../core'))
from core.model import gatherer
from core.model.preprocessing import Formatter


class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        path = '/home/flmoro/research_project/anomaly_detector/tests/data/'
        file = 'raw_normal_traffic.csv'

        self.flows = gatherer.open_csv(path, file, -1, execute_model=True)[0]

    def tearDown(self):
        del self.flows

    def test_Formatter(self):
        features_type = [datetime, datetime, str, str, str, str,
                         str, list, int, int, int, int, int]

        path = '/home/flmoro/research_project/anomaly_detector/tests/data/'
        file = 'formatted_normal_traffic.csv'

        ft = Formatter(self.flows)
        header, flows = ft.format_flows()

        formatted_flows = gatherer.open_csv(path, file, -1, execute_model=True)[0]

        ft = Formatter(formatted_flows)
        result_header, result_flows = ft.format_flows(training_model=True)

        # header length
        self.assertEqual(len(header[0]), len(result_header[0]))

        # features orders and values
        self.assertListEqual(header[0], result_header[0])
        for entry, result_entry in zip(flows, result_flows):
            self.assertListEqual(entry, result_entry)

        # check features instance
        for entry in flows:
            for idx, features in enumerate(entry):
                self.assertIsInstance(features, features_type[idx])

if __name__ == '__main__':
    unittest.main()