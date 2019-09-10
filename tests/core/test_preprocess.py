import os
import sys
import unittest
from datetime import datetime

sys.path.append('/home/flmoro/bsi16/research_project/anomaly_detection/codes/'
                'anomaly_detection_system')

from app.core import gatherer
from app.core import tools
from app.core.preprocess import Formatter, Modifier, Extractor
from app.paths import paths



# defines the main paths use during the tests
formatter_path = f'{paths["test"]}preprocess/formatter/'
modifier_path = f'{paths["test"]}preprocess/modifier/'
extractor_path = f'{paths["test"]}preprocess/extractor/'


# unit tests
class TestFormatter(unittest.TestCase):
    """Tests the Formatter class in preprocess module."""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test functions."""

        # gathering flows
        raw_csv_file = tools.get_content(formatter_path)[1][0]
        header, flows = gatherer.open_csv(formatter_path, raw_csv_file)

        # preprocessing flows
        formatter = Formatter()
        cls.header = formatter.format_header(header)
        cls.flows = formatter.format_flows(flows)

    def test_delete_features(self):
        """Tests if the non-discriminative features were correctly
        deleted."""

        self.assertEqual(len(self.header), 11,
                         'incorrect number of features deleted in header')
        for flow in self.flows:
            self.assertEqual(len(flow), 11,
                             'incorrect number of features deleted in flow')

    def test_sort_features(self):
        """Tests if the features were correctly ordered according to a
        specific pattern."""

        sorted_header = ['ts', 'te', 'sa', 'da', 'pr', 'flg',
                         'sp', 'dp', 'td', 'ipkt', 'ibyt']
        sorted_first_flow = [datetime.strptime('2015-11-24 13:40:37',
                                               '%Y-%m-%d %H:%M:%S'),
                             datetime.strptime('2015-11-24 13:40:39',
                                               '%Y-%m-%d %H:%M:%S'),
                             '146.164.69.172', '146.164.69.255', 'UDP',
                             [0], '631', '631', 2, 3, 678]

        self.assertListEqual(self.header, sorted_header, 'wrong order')
        self.assertListEqual(self.flows[0], sorted_first_flow, 'wrong order')

    def test_replace_features(self):
        """Tests if the missing features were correctly replaced by the
        default values."""

        missing = [datetime.strptime('0001-01-01 01:01:01',
                                     '%Y-%m-%d %H:%M:%S'),
                   datetime.strptime('0001-01-01 01:01:01',
                                     '%Y-%m-%d %H:%M:%S'),
                   '000.000.000.000', '000.000.000.000',
                   'NONE', [0], '0', '0', 0, 0, 0]

        self.assertListEqual(self.flows[1], missing,
                             'missing values filled incorrectly')

    def test_convert_features(self):
        """Tests if the features were correctly converted to a specific
        data type."""

        types = [datetime, datetime, str, str, str,
                 list, str, str, int, int, int]
        for flow in self.flows:
            for feature, type in zip(flow, types):
                self.assertIsInstance(feature, type,
                                      'different instance in flow')

    def test_count_flags(self):
        """Tests if the flags were correctly counted."""

        self.assertListEqual(self.flows[0][5], [0])
        self.assertListEqual(self.flows[3][5], [0, 1, 0, 0, 0, 1])


class TestModifier(unittest.TestCase):
    """Tests the Modifier class in preprocess module."""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test functions."""

        # gathering flows
        raw_csv_file = tools.get_content(modifier_path)[1][-1]
        header, flows = gatherer.open_csv(modifier_path, raw_csv_file)

        # preprocessing flows
        formatter = Formatter()
        header = formatter.format_header(header)
        flows = formatter.format_flows(flows)

        # threshold defined according to the expected result in test dataset
        modifier = Modifier(label=0, threshold=5)
        cls.header = modifier.extend_header(header)
        cls.flows = modifier.aggregate_flows(flows)

    def test_header_order(self):
        """Tests if header order matches new inserts."""

        self.assertEqual(self.header, ['ts', 'te', 'sa', 'da', 'pr',
                                       'flg', 'sp', 'dp', 'td', 'ipkt',
                                       'ibyt', 'bps', 'bpp', 'pps', 'nsp',
                                       'ndp', 'flw', 'lbl'])

    def test_num_features(self):
        """Tests if the flw feature was added."""

        self.assertEqual(len(self.header), 18, 'some features were not added')
        for flow in self.flows:
            self.assertEqual(len(flow), 18, 'some features were not added')

    def test_aggregate_flows(self):
        """Tests if the features were correctly aggregated."""

        # gathering flows
        expt_csv = tools.get_content(modifier_path)[1][0]
        expt_header, expt_flows = gatherer.open_csv(modifier_path, expt_csv)

        # preprocessing flows
        formatter = Formatter(gather=False, train=True)
        expt_flows = formatter.format_flows(expt_flows)

        self.assertListEqual(self.header, expt_header,
                             'aggregation performed incorrectly in header')
        self.assertListEqual(self.flows, expt_flows,
                             'aggregation performed incorrectly in flows')


class TestExtractor(unittest.TestCase):
    """Tests the Extractor class in preprocess module."""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test functions."""

        # gathering flows
        modified_csv_file = tools.get_content(extractor_path)[1][1]
        _, cls.flows = gatherer.open_csv(extractor_path, modified_csv_file)

    def test_extract_features_labels(self):
        """Tests if the features and labels were correctly extracted from
        the flows."""

        # gathering features
        expt_csv = tools.get_content(extractor_path)[1][0]
        expt_features = gatherer.open_csv(extractor_path, expt_csv)[1]

        extractor = Extractor([feature+7 for feature in range(1, 10)])
        features, labels = extractor.extract_features_labels(self.flows)

        self.assertListEqual(features, expt_features,
                             'features extracted incorrectly')
        self.assertEqual(labels[0], '0', 'labels extracted incorrectly')

    def test_extract_specific_features(self):
        """Tests if specifics features and labels were correctly extracted from
        the flows."""

        # gathering features
        expt_csv = tools.get_content(extractor_path)[1][-1]
        expt_features = gatherer.open_csv(extractor_path, expt_csv)[1]

        extractor = Extractor([feature+7 for feature in [1, 3]])
        features, labels = extractor.extract_features_labels(self.flows)

        self.assertListEqual(features, expt_features,
                            'features extracted incorrectly')


# collections of test cases
def formatter_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestFormatter('test_delete_features'))
    suite.addTest(TestFormatter('test_sort_features'))
    suite.addTest(TestFormatter('test_replace_features'))
    suite.addTest(TestFormatter('test_convert_features'))
    suite.addTest(TestFormatter('test_count_flags'))

    return suite


def modifier_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestModifier('test_header_order'))
    suite.addTest(TestModifier('test_num_features'))
    suite.addTest(TestModifier('test_aggregate_flows'))

    return suite


def extractor_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestExtractor('test_extract_features_labels'))
    suite.addTest(TestExtractor('test_extract_specific_features'))

    return suite


# outcome of the test cases
if __name__ == '__main__':
   runner = unittest.TextTestRunner()
   runner.run(formatter_suite())
   runner.run(modifier_suite())
   runner.run(extractor_suite())
