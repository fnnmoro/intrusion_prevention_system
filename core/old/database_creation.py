from core import paths
from model.gatherer import (split_pcap, convert_pcap_nfcapd,
                            convert_nfcapd_csv, open_csv)
from model.preprocess import Formatter
from model.preprocess import Modifier
from model.tools import export_flows_csv, clean_files
from model.walker import menu, DirectoryContents


print('building the dataset', end=f'\n{"-" * 10}\n')

option = menu(['split pcap',
               'convert pcap to nfcapd',
               'convert nfcapd to csv',
               'convert csv to flows',
               'merge flows',
               'clean nfcapd',
               'back to main'])
print(end=f'{"-" * 10}\n')

while option != 7:
    try:
        if option == 1:
            print('splitting file', end=f'\n{"-" * 10}\n')

            dir_cont = DirectoryContents(paths['pcap'])
            path, files = dir_cont.choose_files()

            if not files:
                raise IndexError('error: empty file')

            print(end=f'{"-" * 10}\n')
            split_pcap(path, files, int(input('split size: ')))

            print('split file', end=f'\n{"-" * 10}\n')

        elif option == 2:
            print('converting pcap to nfcapd', end=f'\n{"-" * 10}\n')

            dir_cont = DirectoryContents(paths['pcap'])
            path, files = dir_cont.choose_files()

            if not files:
                raise IndexError('error: empty file')

            print(end=f'{"-" * 10}\n')
            convert_pcap_nfcapd(path, files,
                                         paths['nfcapd'],
                                         int(input('time window size: ')))

            print('converted pcap files', end=f'\n{"-" * 10}\n')

        elif option == 3:
            print('converting nfcapd to csv', end=f'\n{"-" * 10}\n')

            dir_cont = DirectoryContents(paths['nfcapd'])
            path, files = dir_cont.choose_files()

            if not files:
                raise IndexError('error: empty file')

            print(end=f'{"-" * 10}\n')
            convert_nfcapd_csv(path, files,
                                        f'{paths["csv"]}tmp_flows',
                                        input('file name: '))

            print('converted nfcapd files', end=f'\n{"-" * 10}\n')

        elif option == 4:
            print('converting csv to flows', end=f'\n{"-" * 10}\n')

            dir_cont = DirectoryContents(f'{paths["csv"]}tmp_flows')
            path, file = dir_cont.choose_files()

            if not file:
                raise IndexError('error: empty file')

            print(end=f'{"-" * 10}\n')

            header, flows = open_csv(path, file[0],
                                     int(input('sample: ')))

            ft = Formatter(header, flows)
            header = ft.format_header()
            flows = ft.format_flows()

            md = Modifier(flows, header)
            #header, flows = md.aggregate_flows(100)

            print(end=f'{"-" * 10}\n')
            header, flows = md.create_features(int(input('label: ')))

            export_flows_csv(header, flows,
                         f'{paths["csv_path"]}flows',
                         f'{file[0].split(".csv")[0]}_s{len(flows)}'
                         f'.csv')

            print('converted csv file', end=f'\n{"-" * 10}\n')

        elif option == 5:
            print('merging flows', end=f'\n{"-" * 10}\n')

            dataset_name = f'{input("dataset name: ")}.csv'
            print(end=f'{"-" * 10}\n')

            dir_cont = DirectoryContents(f'{paths["csv_path"]}flows')
            path, files = dir_cont.choose_files()

            if not files:
                raise IndexError('error: empty file')

            print(end=f'{"-" * 10}\n')

            for idx, file in enumerate(files):
                header, flows = open_csv(path, file)

                export_flows_csv(header, flows,
                                 f'{paths["csv"]}datasets/',
                                 f'{dataset_name}')

            print('merged flows', end=f'\n{"-" * 10}\n')

        elif option == 6:
            print('cleaning nfcapd files', end=f'\n{"-" * 10}\n')

            clean_files([paths["nfcapd"]])

            print('cleaned nfcapd files', end=f'\n{"-" * 10}\n')

        elif option == 7:
            break
        else:
            print('invalid option', end=f'\n{"-" * 10}\n')
    except IndexError as error:
        print(end=f'{"-" * 10}\n')
        print(error)
        print(end=f'{"-" * 10}\n')

    option = menu(['split pcap',
                   'convert pcap to nfcapd',
                   'convert nfcapd to csv',
                   'convert csv to flows',
                   'merge flows',
                   'clean nfcapd',
                   'back to main'])
    print(end=f'{"-" * 10}\n')

print('built dataset', end=f'\n{"-" * 10}\n')
