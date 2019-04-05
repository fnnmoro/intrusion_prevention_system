import os
import sys
import csv
import time
import unittest
from math import ceil
from datetime import datetime
from core.model.gatherer import (split_pcap, convert_pcap_nfcapd,
                                 convert_nfcapd_csv, open_csv,
                                 capture_nfcapd)
from core.model.tools import clean_files
from core.model.walker import get_files


# defines the main paths use during the tests
base_path = ('/home/flmoro/bsi16/research_project/anomaly_detection/codes/'
             'triple_m_ads/tests/data/gatherer/')
pcap_path = f'{base_path}pcap/'
nfcapd_path = f'{base_path}nfcapd/'
csv_path = f'{base_path}csv/'


# unit tests
class TestSplitPcap(unittest.TestCase):
    """Tests the split_pcap function in gatherer module"""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test function"""

        cls.pcap_file = 'normal_traffic1_0.pcap'
        cls.split_size = 300

        # function to be tested
        split_pcap(pcap_path, [cls.pcap_file], cls.split_size)

    @classmethod
    def tearDownClass(cls):
        """Cleans all files used in tests"""

        clean_files([f'{pcap_path}split/'], ['*'])
        os.system(f'rm -rf {pcap_path}split')

    def test_num_files(self):
        """Tests the number of files created by splitting the pcap files"""

        self.assertEqual(len(get_files(f'{pcap_path}split/')), 4,
                         'different number of pcap files')

    def test_last_file_size(self):
        """Tests if the last file generated has the expected remaining size"""

        pcap_files = get_files(f'{pcap_path}split/')

        last_file_size = os.path.getsize(f'{pcap_path}split/'
                                         f'{pcap_files[-1]}')

        # converts the last file size to megabytes and then rounded up
        self.assertEqual(ceil(last_file_size/(1000**2)), 173,
                         'different size of the last file')


class TestConvertPcapNfcapd(unittest.TestCase):
    """Tests the convert_pcap_nfcapd function in gatherer module"""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test function"""

        pcap_file = 'normal_traffic1_0.pcap'

        # function to be tested
        convert_pcap_nfcapd(pcap_path, [pcap_file], nfcapd_path, 60)

    @classmethod
    def tearDownClass(cls):
        """Cleans all files used in tests"""

        clean_files([f'{nfcapd_path}'], ['*'])

    def test_num_files(self):
        """Tests if the number of files match if the number of minutes in the
        pcap file"""

        self.assertEqual(len(get_files(nfcapd_path)), 14,
                         'different number of nfcapd files')

    def test_time_interval(self):
        """Tests if the time interval between the nfcapd files is according to
        the defined time"""

        nfcapd_files = get_files(nfcapd_path)

        # gets the minutes in the nfcapd file name
        minutes = [int(file.split('.')[-1][-2:]) for file in nfcapd_files]

        # checks if all files have the same time interval
        for x, y in zip(minutes[:-1], minutes[1:]):
            self.assertEqual(y-x, 1, 'wrong time interval')


class TestConvertNfcapdCSV(unittest.TestCase):
    """Tests the convert_nfcapd_csv function in gatherer module"""

    def setUp(self):
        """Initiates the parameters to feed the test function and previous
        function to generated the necessary files"""

        pcap_file = 'normal_traffic1_0.pcap'

        convert_pcap_nfcapd(pcap_path, [pcap_file], nfcapd_path, 60)

        nfcapd_files = get_files(nfcapd_path)

        convert_nfcapd_csv(nfcapd_path, nfcapd_files, csv_path, 'test')

    def tearDown(self):
        """Cleans all files used in tests"""

        clean_files([f'{nfcapd_path}'], ['*'])
        clean_files([f'{csv_path}'], ['*'])

    def test_file_interval(self):
        """Tests if the csv file interval generate by the nfcapd files is
        correct"""

        csv_file = get_files(csv_path)[0]

        flows = list()
        with open(f'{csv_path}{csv_file}') as file:
            reader = csv.reader(file)

            for line in reader:
                flows.append(line)

        # gets the first and last minute of the flows to check the interval
        start_time = datetime.strptime(flows[1][0],
                                       '%Y-%m-%d %H:%M:%S').minute
        final_time = datetime.strptime(flows[-4][0],
                                       '%Y-%m-%d %H:%M:%S').minute

        self.assertEqual(final_time-start_time, 13, 'wrong file interval')


class TestOpenCSV(unittest.TestCase):
    """Tests the open_csv function in gatherer module"""

    @classmethod
    def setUpClass(cls):
        """Initiates the parameters to feed the test function and previous
        functions to generated the necessary files"""

        pcap_file = 'normal_traffic1_0.pcap'

        convert_pcap_nfcapd(pcap_path, [pcap_file], nfcapd_path, 60)

        nfcapd_files = get_files(nfcapd_path)

        convert_nfcapd_csv(nfcapd_path, nfcapd_files, csv_path, 'test')

        csv_file = get_files(csv_path)[0]

        cls.header, cls.flows = open_csv(csv_path, csv_file, 30)

    @classmethod
    def tearDownClass(cls):
        """Cleans all files used in tests"""

        clean_files([f'{nfcapd_path}'], ['*'])
        clean_files([f'{csv_path}'], ['*'])

    def test_header_length(self):
        """Tests the length of the header based on the number of features"""

        self.assertEqual(len(self.header), 48)

    def test_flow_length(self):
        """Tests the length of the flow based on the number of features"""

        self.assertEqual(len(self.flows[0]), 48)

    def test_num_flows(self):
        """Tests the number of flows to verify the sample process"""

        self.assertEqual(len(self.flows), 30)

    def test_last_flow(self):
        """Tests the values of the features from the last flow"""

        last_flow = ['2015-11-24 13:40:52', '2015-11-24 13:40:52', '0.000',
                     '146.164.69.203', '224.0.0.251', '0', '0', 'IGMP',
                     '......', '0', '0', '1', '8', '0', '0', '0', '0', '0',
                     '0', '0', '0', '0', '0', '0.0.0.0', '0.0.0.0', '0', '0',
                     '00:00:00:00:00:00', '00:00:00:00:00:00',
                     '00:00:00:00:00:00', '00:00:00:00:00:00',
                     '0-0-0', '0-0-0', '0-0-0', '0-0-0', '0-0-0', '0-0-0',
                     '0-0-0', '0-0-0', '0-0-0', '0-0-0', '    0.000',
                     '    0.000', '    0.000', '0.0.0.0', '0/0', '0',
                     '1969-12-31 21:00:00.000']

        self.assertListEqual(self.flows[-1], last_flow)


class TestCaptureNfcapd(unittest.TestCase):
    """Tests the capture_nfcapd function in gatherer module"""

    def setUp(self):
        """Initiates the parameters to feed the test function"""

        self.process = capture_nfcapd(nfcapd_path, 60)

    def tearDown(self):
        """Cleans all files used in tests and kills the process started by the
        function"""

        clean_files([f'{nfcapd_path}'], ['*'])
        self.process.kill()

    def test_file_creation(self):
        """Tests if the process started by the function is creating the files
        correctly"""

        # delay one second to allow the start of the process
        time.sleep(1)
        self.assertIn('nfcapd.current', get_files(nfcapd_path)[0])


# collections of test cases
def split_pcap_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestSplitPcap('test_num_files'))
    suite.addTest(TestSplitPcap('test_last_file_size'))

    return suite


def convert_pcap_nfcapd_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestConvertPcapNfcapd('test_num_files'))
    suite.addTest(TestConvertPcapNfcapd('test_time_interval'))

    return suite


def convert_nfcapd_csv_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestConvertNfcapdCSV('test_file_interval'))

    return suite


def open_csv_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestOpenCSV('test_header_length'))
    suite.addTest(TestOpenCSV('test_flow_length'))
    suite.addTest(TestOpenCSV('test_num_flows'))
    suite.addTest(TestOpenCSV('test_last_flow'))

    return suite


def capture_nfcapd_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCaptureNfcapd('test_file_creation'))

    return suite

# outcome of the test cases
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(split_pcap_suite())
    runner.run(convert_pcap_nfcapd_suite())
    runner.run(convert_nfcapd_csv_suite())
    runner.run(open_csv_suite())
    # requires the simulation of a software-defined networking
    runner.run(capture_nfcapd_suite())
