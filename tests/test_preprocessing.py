import os
import sys
import unittest
from datetime import datetime
sys.path.append(os.path.abspath('../core'))
from core.model import gatherer
from core.model.preprocessing import Formatter, Modifier, Extractor


class TestFormatter(unittest.TestCase):

    def setUp(self):
        path = '/home/flmoro/bsi16/research_project/codes/anomaly_detector/tests/data/'
        file = 'raw_normal_traffic.csv'

        # flows to be tested with an existent existing file
        flows = gatherer.open_csv(path, file, -1, True)[0]

        ft = Formatter(flows)
        self.header, self.flows = ft.format_flows(0)

        # file with the expected result
        path = '/home/flmoro/bsi16/research_project/codes/anomaly_detector/tests/data/'
        file = 'formatted_normal_traffic.csv'

        # flows with the result
        result_flows = gatherer.open_csv(path, file, -1, True)[0]

        ft = Formatter(result_flows)
        self.result_header, self.result_flows = ft.format_flows(True, True)

    def tearDown(self):
        del self.flows

    def test_header_length(self):
        # header length
        self.assertEqual(len(self.header[0]), len(self.result_header[0]))

    def test_features_type(self):
        features_type = [datetime, datetime, str, str, str, str,
                         str, list, int, int, int, int, int, int, int]

        # check features instance
        for entry in self.flows:
            for idx, features in enumerate(entry):
                self.assertIsInstance(features, features_type[idx])

    def test_format_flows(self):
        # features values
        self.assertListEqual(self.header[0], self.result_header[0])

        for entry, result_entry in zip(self.flows, self.result_flows):
            self.assertListEqual(entry, result_entry)


class TestModifier(unittest.TestCase):

    def setUp(self):
        path = '/home/flmoro/bsi16/research_project/codes/anomaly_detector/tests/data/'
        file = 'raw_normal_traffic.csv'

        # flows to be tested with an existent existing file
        flows = gatherer.open_csv(path, file, -1, True)[0]

        ft = Formatter(flows)
        header, flows = ft.format_flows(0)

        md = Modifier(flows, header)
        self.header, self.flows = md.modify_flows(10, True)

        # file with the expected result
        path = '/home/flmoro/bsi16/research_project/codes/anomaly_detector/tests/data/'
        file = 'aggregated_normal_traffic.csv'

        result_flows = gatherer.open_csv(path, file, -1, True)[0]

        ft = Formatter(result_flows)
        self.result_header, self.result_flows = ft.format_flows(True, True)

    def test_header_length(self):
        # header length
        self.assertEqual(len(self.header[0]), len(self.result_header[0]))

    def test_features_type(self):
        features_type = [datetime, datetime, str, str, str, str, str, list,
                         int, int, int, int, int, int, int, int, int, int]

        # check features instance
        for entry in self.flows:
            for idx, features in enumerate(entry):
                self.assertIsInstance(features, features_type[idx])

    def test_modify_flows(self):
        # features values
        self.assertListEqual(self.header[0], self.result_header[0])

        for entry, result_entry in zip(self.flows, self.result_flows):
            self.assertListEqual(entry, result_entry)


class TestExtractor(unittest.TestCase):

    def setUp(self):
        path = '/home/flmoro/bsi16/research_project/codes/anomaly_detector/tests/data/'
        file = 'raw_normal_traffic.csv'

        flows = gatherer.open_csv(path, file, -1, True)[0]

        ft = Formatter(flows)
        header, flows = ft.format_flows(0)

        md = Modifier(flows, header)
        header, flows = md.modify_flows(100, True)

        ex = Extractor()
        self.header_features, self.features = ex.extract_features(header, flows,
                list(range(8, 17)))
        self.labels = ex.extract_labels(flows)

        # file with the expected result
        path = '/home/flmoro/bsi16/research_project/codes/anomaly_detector/tests/data/'
        file = 'aggregated_normal_traffic.csv'

        result_flows = gatherer.open_csv(path, file, -1, True)[0]

        ft = Formatter(result_flows)
        self.result_header, self.result_flows = ft.format_flows(True, True)

    def test_header_length(self):
        # header length
        self.assertEqual(len(self.header_features[0]),
                         len(self.result_header[0][8:17]))

    def test_extract_features(self):
        for entry, result_entry in zip(self.features, self.result_flows):
            self.assertListEqual(entry, result_entry[8:17])

    def test_extract_label(self):
        for entry, result_entry in zip(self.labels, self.result_flows):
            self.assertEqual(entry, result_entry[-1])


def formatter_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestFormatter('test_header_length'))
    suite.addTest(TestFormatter('test_features_type'))
    suite.addTest(TestFormatter('test_format_flows'))

    return suite


def modifier_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestModifier('test_header_length'))
    suite.addTest(TestModifier('test_features_type'))
    suite.addTest(TestModifier('test_modify_flows'))

    return suite


def extractor_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestExtractor('test_header_length'))
    suite.addTest(TestExtractor('test_extract_features'))
    suite.addTest(TestExtractor('test_extract_label'))

    return suite


if __name__ == '__main__':
   runner = unittest.TextTestRunner()
   runner.run(formatter_suite())
   runner.run(modifier_suite())
   runner.run(extractor_suite())