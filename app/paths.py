import os


root = f'{os.path.abspath(os.path.dirname("anomaly_detection_system"))}/data/'

paths = {'csv': f'{root}' + 'csv/',
         'log': f'{root}' + 'log/',
         'nfcapd': f'{root}' + 'nfcapd/',
         'pcap': f'{root}' + 'pcap/',
         'models': f'{root}' + 'models/',
         'test': f'{root}' + 'test/'}
