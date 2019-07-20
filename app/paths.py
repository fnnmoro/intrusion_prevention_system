import os


root = f'{os.path.abspath(os.path.dirname("anomaly_detection_system"))}/data/'

paths = {'csv': f'{root}' + 'csv/',
         'log': f'{root}' + 'log/',
         'nfcapd': f'{root}' + 'nfcapd/',
         'pcap': f'{root}' + 'pcap/',
         'saves': f'{root}' + 'saves/',
         'test': f'{root}' + 'test/'}
