import os
import csv
import subprocess
from .tools import make_dir, processing_time_log


def split_pcap(pcap_path, pcap_files, split_size):
    """Splits pcap files according to the chosen size.

    Parameters
    ----------
    pcap_path: str
        Absolute pcap path.
    pcap_files: list
        All pcap files to be split.
    split_size: int
        Size of the split.

    Raises
    ----------
    subprocess.CalledProcessError
        Entered a invalid value less or equal to zero."""

    try:
        make_dir(f'{pcap_path}/split/')

        for pcap_file in pcap_files:
            # runs tcpdump program to split the pcap files
            subprocess.run(f'tcpdump -r {pcap_path}/{pcap_file} -w '
                           f'{pcap_path}/split/{pcap_file.split(".pcap")[0]} '
                           f'-C {split_size}',
                           shell=True, check=True)

            print(pcap_path + pcap_file, end=f'\n{"-" * 10}\n')

        # renames all split pcap files
        for file in sorted(os.listdir(f'{pcap_path}/split/')):
            os.rename(f'{pcap_path}/split/{file}',
                      f'{pcap_path}/split/{file}.pcap')
    except subprocess.CalledProcessError:
        print('split size must be greater than 0', end=f'\n{"-" * 10}\n')


def convert_pcap_nfcapd(pcap_path, pcap_files, nfcapd_path, win_time):
    """Converts pcap files to nfcapd files.

    Parameters
    ----------
    pcap_path: str
        Absolute pcap path.
    pcap_files: list
        All pcap files to be converted.
    nfcapd_path: str
        Absolute nfcapd path.
    win_time: int
        Size of the window time.

    Raises
    ----------
    subprocess.CalledProcessError
        Entered a invalid value less or equal to zero."""

    try:
        for pcap_file in pcap_files:
            print(f'{pcap_path}/{pcap_file}', end=f'\n{"-" * 10}\n')

            # runs nfpcapd program to convert pcap files to nfcapd files
            subprocess.run(f'nfpcapd -t {win_time} -T all '
                           f'-r {pcap_path}/{pcap_file} -l {nfcapd_path}',
                           shell=True, check=True)

    except subprocess.CalledProcessError:
        print('time window size must be greater than 0', end=f'\n{"-" * 10}\n')


def convert_nfcapd_csv(nfcapd_path, nfcapd_files, csv_path, file_name):
    """Converts nfcapd files to csv files.

    Parameters
    ----------
    nfcapd_path: str
        Absolute nfcapd path.
    nfcapd_files: list
        All nfcapd files to be split.
    csv_path: str
        Absolute csv path.
    file_name: str
        Name of csv file."""

    file_name = f'{file_name}_' \
                f'{nfcapd_files[0].split("nfcapd.")[1]}_'\
                f'{nfcapd_files[-1].split("nfcapd.")[1]}.csv'

    print(f'{nfcapd_path}/{nfcapd_files[0]}:{nfcapd_files[-1]}',
          end=f'\n{"-" * 10}\n')

    # runs nfdump program to convert nfcapd files to csv
    subprocess.run(f'nfdump -O tstart -o csv -6 -R {nfcapd_path}/'
                   f'{nfcapd_files[0]}:{nfcapd_files[-1]} > '
                   f'{csv_path}{file_name}',
                   shell=True, check=True)


@processing_time_log
def open_csv(csv_path, csv_files, sample=-1, execute_model=False):
    """Opens a CSV file containing raw flows"""
    try:
        if execute_model == False:
            print()
            idx = int(input("choose csv file: "))-1
            print()

            csv_files = csv_files[idx]

            print(csv_path + csv_files, end="\n\n")

        with open(csv_path + csv_files, mode='r') as file:
            csv_file = csv.reader(file)
            flows = []
            count = 0

            for line in csv_file:
                # checks if the core number has been reached
                if count != sample:
                    # checks if is not the last line
                    if "Summary" not in line[0]:
                        flows.append(line)
                        count += 1
                    # break if the last line was found
                    else:
                        break
                # break if the core was reached
                else:
                    break
            return flows, csv_files
    except IndexError as error:
        print()
        print(error, end="\n\n")


def nfcapd_collector(nfcapd_path, win_time=0):
    try:
        process = subprocess.Popen(["nfcapd", "-t", str(win_time), "-T",
                                    "all", "-b", "127.0.0.1", "-p", "7777",
                                    "-l", nfcapd_path],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        return process
    except subprocess.CalledProcessError as error:
        print()
        print(error, end="\n\n")
