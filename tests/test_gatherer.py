import os
import sys
import unittest
sys.path.append(os.path.abspath('../core'))
from core.model import gatherer

class TestOpenCSV(unittest.TestCase):

    def setUp(self):
        path = '/home/flmoro/research_project/anomaly_detector/tests/data/'
        file = 'raw_normal_traffic.csv'

        self.flows = gatherer.open_csv(path, file, -1, execute_model=True)[0]

    def tearDown(self):
        del self.flows

    def test_header_length(self):
        # header length
        self.assertEqual(len(self.flows[0]), 48)

    def test_num_entries(self):
        # number of entries
        self.assertEqual(len(self.flows), 23)


if __name__ == '__main__':
    unittest.main()