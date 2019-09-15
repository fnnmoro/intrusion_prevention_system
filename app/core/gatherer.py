import csv
import os
import subprocess

from app.core import util


def split_pcap(pcap_path, pcap_files, split_size):
    """Splits pcap files according to a chosen size.

    To perform subsequent actions,larger pcap files must be split.

    It will be created inside the pcap folder a new folder with the split pcap
    files.

    Parameters
    ----------
    pcap_path: str
        Absolute pcap path.
    pcap_files: list
        One or many pcap file to be split.
    split_size: int
        Size of the split. The units are milions of bytes (1000000 bytes).

    Raises
    ----------
    subprocess.CalledProcessError
        Entered a invalid value less or equal to zero in the split size."""

    try:
        directory = f'split_{pcap_files[0].split("_")[0]}'
        directory = util.make_directory(pcap_path, directory)

        for pcap_file in pcap_files:
            # runs tcpdump program to split the pcap files.
            subprocess.run(f'tcpdump -r {pcap_path}{pcap_file} -w '
                           f'{pcap_path}{directory}'
                           f'{pcap_file.split(".pcap")[0]} '
                           f'-C {split_size}',
                           shell=True, check=True)

        # renames all split pcap files.
        for file in sorted(os.listdir(f'{pcap_path}{directory}')):
            os.rename(f'{pcap_path}{directory}{file}',
                      f'{pcap_path}{directory}/{file}.pcap')
    except subprocess.CalledProcessError:
        print('split size must be greater than 0', end=f'\n{"-" * 10}\n')


def convert_pcap_nfcapd(pcap_path, pcap_files, nfcapd_path, time_interval):
    """Converts pcap files to nfcapd files according to a time interval.

    The nfcapd files created will be stored in the nfcapd folder.

    Parameters
    ----------
    pcap_path: str
        Absolute pcap path.
    pcap_files: list
        One or many pcap files to be converted.
    nfcapd_path: str
        Absolute nfcapd path to store the generated files.
    time_interval: int
        Duration of the time interval in seconds to rotate files.

    Raises
    ----------
    subprocess.CalledProcessError
        Entered a invalid value less or equal to zero in time interval."""

    try:
        for pcap_file in pcap_files:
            # runs nfpcapd program to convert pcap files to nfcapd files.
            subprocess.run(f'nfpcapd -t {time_interval} -T all '
                           f'-r {pcap_path}{pcap_file} -l {nfcapd_path}',
                           shell=True, check=True)

    except subprocess.CalledProcessError:
        print('the duration of the time interval must be greater than 0',
        end=f'\n{"-" * 10}\n')


def convert_nfcapd_csv(nfcapd_path, nfcapd_files, csv_path, file_name):
    """Converts nfcapd files to csv file.

    The csv file will be created based on one or multiple nfcapd files and will
    be stored in the csv folder.

    Parameters
    ----------
    nfcapd_path: str
        Absolute nfcapd path.
    nfcapd_files: list
        One or many nfcapd files to be converted.
    csv_path: str
        Absolute CSV path.
    file_name: str
        Name of CSV file."""

    file_name = f'{file_name}_' \
                f'{nfcapd_files[0].split("nfcapd.")[1]}_'\
                f'{nfcapd_files[-1].split("nfcapd.")[1]}.csv'

    # runs nfdump program to convert nfcapd files to csv.
    subprocess.run(f'nfdump -O tstart -o csv -6 -R {nfcapd_path}'
                   f'{nfcapd_files[0]}:{nfcapd_files[-1]} > '
                   f'{csv_path}{file_name}',
                   shell=True, check=True)


@util.timing
def open_csv(csv_path, csv_file, sample_size=-1):
    """Opens CSV file.

    The CSV file must contain IP flows with header.

    Parameters
    ----------
    csv_path: list
        Absolute CSV path.
    csv_file: list
        CSV file to be open.
    sample_size: int
        Sample size. -1 for all lines.

    Returns
    -------
    list
        Header and IP flows"""

    flows = list()

    with open(f'{csv_path}{csv_file}') as file:
        reader = csv.reader(file)
        header = next(reader)

        for idx, line in enumerate(reader):
            # checking if sample was reached.
            if idx != sample_size:
                flows.append(line)
            else:
                break

    return header, flows


def capture_nfcapd(nfcapd_path, win_time):
    """Captures netflow data from the network according to a time interval and
    store into nfcapd files.

    The generated nfcapd files will be stored in the nfcapd folder.

    Parameters
    ----------
    nfcapd_path: list
        Absolute nfcapd path.
    time_interval: list
        Duration of the time interval in seconds to rotate files.

    Returns
    -------
    object
        Popen instance."""

    try:
        process = subprocess.Popen(['nfcapd', '-t', str(win_time), '-T',
                                    'all', '-b', '127.0.0.1', '-p', '7777',
                                    '-l', nfcapd_path],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)

        return process
    except subprocess.CalledProcessError:
        print('the duration of the time interval must be greater than 0',
        end=f'\n{"-" * 10}\n')
