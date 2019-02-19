import os
import csv
import subprocess
from model.tools import make_dir, process_time_log


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
        make_dir(f'{pcap_path}split/')

        for pcap_file in pcap_files:
            # runs tcpdump program to split the pcap files
            subprocess.run(f'tcpdump -r {pcap_path}{pcap_file} -w '
                           f'{pcap_path}split/{pcap_file.split(".pcap")[0]} '
                           f'-C {split_size}',
                           shell=True, check=True)

            print(pcap_path + pcap_file, end=f'\n{"-" * 10}\n')

        # renames all split pcap files
        for file in sorted(os.listdir(f'{pcap_path}split/')):
            os.rename(f'{pcap_path}split/{file}',
                      f'{pcap_path}split/{file}.pcap')
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
            print(f'{pcap_path}{pcap_file}', end=f'\n{"-" * 10}\n')

            # runs nfpcapd program to convert pcap files to nfcapd files
            subprocess.run(f'nfpcapd -t {win_time} -T all '
                           f'-r {pcap_path}{pcap_file} -l {nfcapd_path}',
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
        All nfcapd files to be converted.
    csv_path: str
        Absolute CSV path.
    file_name: str
        Name of CSV file."""

    file_name = f'{file_name}_' \
                f'{nfcapd_files[0].split("nfcapd.")[1]}_'\
                f'{nfcapd_files[-1].split("nfcapd.")[1]}.csv'

    print(f'{nfcapd_path}{nfcapd_files[0]}:{nfcapd_files[-1]}',
          end=f'\n{"-" * 10}\n')

    # runs nfdump program to convert nfcapd files to csv
    subprocess.run(f'nfdump -O tstart -o csv -6 -R {nfcapd_path}'
                   f'{nfcapd_files[0]}:{nfcapd_files[-1]} > '
                   f'{csv_path}{file_name}',
                   shell=True, check=True)


@process_time_log
def open_csv(csv_path, csv_file, sample=-1):
    """Opens CSV file.

    Parameters
    ----------
    csv_path: list
        Absolute CSV path.
    csv_file: list
        CSV file to be open.
    sample: int
        Number of sampling lines. -1 for all lines.

    Returns
    -------
    list
        IP flows header.
    list
        IP flows."""

    flows = list()

    with open(f'{csv_path}{csv_file}') as reader:
        reader = csv.reader(reader)
        header = next(reader)

        for idx, line in enumerate(reader):
            # adds lines until sample was reached
            if idx != sample:
                flows.append(line)
            else:
                break
        return header, flows


def capture_nfcapd(nfcapd_path, win_time):
    """Captures netflow data and store into nfcapd files.

    Parameters
    ----------
    nfcapd_path: list
        Absolute nfcapd path.
    win_time: list
        Size of the window time.

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
        print('time window size must be greater than 0', end=f'\n{"-" * 10}\n')
