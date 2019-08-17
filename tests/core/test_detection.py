import os
import sys
import unittest
from datetime import datetime

sys.path.append('/home/flmoro/bsi16/research_project/anomaly_detection/codes/'
                'anomaly_detection_system')

from app.core import gatherer
from app.core import tools
from app.core.detection import Detector
from app.core.preprocess import Formatter
from app.paths import paths


# defines the main paths use during the tests
detector_path = f'{paths["test"]}detection/detector/'


# unit tests
class TestDetector(unittest.TestCase):
    """Tests the Detector class in preprocess module."""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test functions."""

        # gathering flows
        raw_csv_file = tools.get_content(detector_path)[1][0]
        _, flows = gatherer.open_csv(detector_path, raw_csv_file)

        # preprocessing flows
        for entry in flows:
            Formatter.convert_features(entry, True)
        pred = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0]

        detector = Detector(None)
        cls.intrusions = detector.find_intrusions(flows, pred)

    def test_find_intrusions(self):
        """Tests if intrusions are correctly found."""

        csv_result = tools.get_content(detector_path)[1][1]
        _, expected_intrusions = gatherer.open_csv(detector_path, csv_result)

        for entry in expected_intrusions:
            Formatter.convert_features(entry, True)

        self.assertEqual(len(self.intrusions), 3,
                        'incorrect number of intrusions')
        self.assertListEqual(self.intrusions, expected_intrusions,
                             'incorrect intrusions found')


# collections of test cases
def detector_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDetector('test_find_intrusions'))

    return suite


# outcome of the test cases
if __name__ == '__main__':
   runner = unittest.TextTestRunner()
   runner.run(detector_suite())
