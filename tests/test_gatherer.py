import os
import sys
import unittest
sys.path.append(os.path.abspath('../core'))
from core.model import gatherer

class TestGatherer(unittest.TestCase):

    def test_open_csv(self):
        path = '/home/flmoro/research_project/anomaly_detector/tests/data/'
        file = 'raw_normal_traffic.csv'

        flows = gatherer.open_csv(path, file, -1, execute_model=True)[0]

        # header length
        self.assertEqual(len(flows[0]), 48)
        # number of entries
        self.assertEqual(len(flows), 23)

if __name__ == '__main__':
    unittest.main()