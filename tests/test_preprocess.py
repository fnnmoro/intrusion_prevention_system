import os
import sys
import unittest
from datetime import datetime
from core.model.gatherer import open_csv
from core.model.preprocess import Formatter, Modifier, Extractor, Preprocessor
from core.model.tools import clean_files
from core.model.walker import get_files


# defines the main paths use during the tests
base_path = ('/home/flmoro/bsi16/research_project/anomaly_detection/codes/'
             'triple_m_ads/tests/data/preprocess/')
formatter_path = f'{base_path}formatter/'
modifier_path = f'{base_path}modifier/'
extractor_path = f'{base_path}extractor/'


# unit tests
class TestFormatter(unittest.TestCase):
    """Tests the Formatter class in preprocess module."""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test functions."""

        raw_csv_file = get_files(formatter_path)[0]

        header, flows = open_csv(formatter_path, raw_csv_file)

        formatter = Formatter(header, flows)
        cls.header = formatter.format_header()
        cls.flows = formatter.format_flows()

    def test_delete_features(self):
        """Tests whether the non-discriminative features were correctly
        deleted."""

        self.assertEqual(len(self.header), 11,
                         'incorrect number of features deleted in header')

        for flow in self.flows:
            self.assertEqual(len(flow), 11,
                             'incorrect number of features deleted in flow')

    def test_sort_features(self):
        """Tests whether the features were correctly ordered according to a
        specific pattern."""

        sorted_header = ['ts', 'te', 'sa', 'da', 'pr', 'flg',
                         'sp', 'dp', 'td', 'ipkt', 'ibyt']

        sorted_first_flow = [datetime.strptime('2015-11-24 13:40:37',
                                               '%Y-%m-%d %H:%M:%S'),
                             datetime.strptime('2015-11-24 13:40:39',
                                               '%Y-%m-%d %H:%M:%S'),
                             '146.164.69.172', '146.164.69.255', 'udp',
                             [0], 631, 631, 2, 3, 678]

        self.assertListEqual(self.header, sorted_header, 'wrong order')
        self.assertListEqual(self.flows[0], sorted_first_flow, 'wrong order')

    def test_replace_features(self):
        """Tests whether the missing features were correctly replaced by the
        default values."""

        missing = [datetime.strptime('0001-01-01 01:01:01',
                                     '%Y-%m-%d %H:%M:%S'),
                   datetime.strptime('0001-01-01 01:01:01',
                                     '%Y-%m-%d %H:%M:%S'),
                   '000.000.000.000', '000.000.000.000',
                   'nopr', [0], 0, 0, 0, 0, 0]

        self.assertListEqual(self.flows[1], missing,
                             'missing values filled incorrectly')

    def test_convert_features(self):
        """Tests whether the features were correctly converted to a specific
        data type."""

        types = [datetime, datetime, str, str, str,
                 list, int, int, int, int, int]

        for flow in self.flows:
            for feature, type in zip(flow, types):
                self.assertIsInstance(feature, type,
                                      'different instance in flow')

    def test_count_flags(self):
        """Tests whether the flags were correctly counted."""

        self.assertListEqual(self.flows[0][5], [0])
        self.assertListEqual(self.flows[3][5], [0, 1, 0, 0, 0, 1])


class TestModifier(unittest.TestCase):
    """Tests the Modifier class in preprocess module."""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test functions."""

        raw_csv_file = get_files(modifier_path)[2]

        header, flows = open_csv(modifier_path, raw_csv_file)

        formatter = Formatter(header, flows)
        header = formatter.format_header()
        flows = formatter.format_flows()

        cls.modifier = Modifier(flows, header)
        # threshold defined according to the expected result in test dataset
        cls.header, cls.flows = cls.modifier.aggregate_flows(5)

    def test_num_new_features(self):
        """Tests whether the flw feature was added."""

        self.assertEqual(len(self.header), 12, 'flw feature it was not added')
        for flow in self.flows:
            self.assertEqual(len(flow), 12, 'flw feature it was not added')

    def test_aggregate_flows(self):
        """Tests whether the features were correctly aggregated."""

        csv_result = get_files(modifier_path)[0]

        # expected result
        header, expected_flows = open_csv(modifier_path, csv_result)

        for entry in expected_flows:
            Formatter.convert_features(entry, True)

        self.assertListEqual(self.flows, expected_flows,
                             'aggregation performed incorrectly')

    def test_create_features(self):
        """Tests whether the new features were correctly created."""

        csv_result = get_files(modifier_path)[1]

        # expected result
        expected_header, expected_flows = open_csv(modifier_path, csv_result)

        for entry in expected_flows:
            Formatter.convert_features(entry, True)

        # features creation
        header, flows = self.modifier.create_features(0)

        self.assertListEqual(header, expected_header,
                             'creation performed incorrectly in header')
        self.assertListEqual(flows, expected_flows,
                             'creation performed incorrectly in flows')


class TestExtractor(unittest.TestCase):
    """Tests the Extractor class in preprocess module."""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test functions."""

        modified_csv_file = get_files(extractor_path)[1]

        header, flows = open_csv(extractor_path, modified_csv_file)

        cls.extractor = Extractor(6, list(range(9)))        
        cls.features, cls.labels = cls.extractor.extract_features(flows)

    def test_extract_features(self):
        """Tests whether the features and labels were correctly extracted from
        the flows."""

        csv_result = get_files(extractor_path)[0]

        expected_features = open_csv(extractor_path, csv_result)[1]

        self.assertListEqual(self.features, expected_features,
                             'features extracted incorrectly')
        self.assertEqual(self.labels[0], '0',
                         'labels extracted incorrectly')


class TestPreprocessor(unittest.TestCase):
    """Tests the Preprocessor class in preprocess module."""

    def setUp(self):
        """Initiates the parameters to feed the test functions."""

        self.methods = Preprocessor.methods

    def test_select_method(self):
        """Tests whether the constructor of a preprocessing method were
        correctly selected.."""

        from sklearn.preprocessing import MinMaxScaler

        self.assertEqual(type(MinMaxScaler()),
                         type(self.methods['minmax scaler']),
                         'preprocessing method selected incorrectly')


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
    suite.addTest(TestModifier('test_num_new_features'))
    suite.addTest(TestModifier('test_aggregate_flows'))
    suite.addTest(TestModifier('test_create_features'))

    return suite


def extractor_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestExtractor('test_extract_features'))

    return suite


def preprocessor_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPreprocessor('test_select_method'))

    return suite


# outcome of the test cases
if __name__ == '__main__':
   runner = unittest.TextTestRunner()
   runner.run(formatter_suite())
   runner.run(modifier_suite())
   runner.run(extractor_suite())
   runner.run(preprocessor_suite())
