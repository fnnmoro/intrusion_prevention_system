import os
import csv
import time
from datetime import datetime
from core import paths


def make_dir(path):
    """Creates a directory, if it not exists.

    Parameters
    ----------
    path: str
        Absolute path."""

    if not os.path.exists(path):
        os.system(f'mkdir {path}')


def export_flows(header, flows, dst_path, file_name):
    """Exports flows to CSV file.

    Parameters
    ----------
    header: list
        Features description.
    flows: list
        IP flows.
    dst_path: str
        Destination path where the file will be exported.
    file_name: str
        Name of CSV file."""

    with open(dst_path + file_name, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(header)

        for entry in flows:
            writer.writerow(entry)


def process_time_log(func):
    """Decorator to record the time of a function.

    Parameters
    ----------
    func: func
        Function.

    Returns
    -------
    func
        Timer function to processes the time of a function"""

    def timer(*args, **kwargs):
        """Processes the time of a function.

        Parameters
        ----------
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        list
            If the function passed as an argument is to train or execute the
            classifier, the return will be the normal return of the function,
            date and duration.

            Otherwise only the normal return of the passed function as argument
            will be returned."""

        date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        start = time.time()

        # function passed as an argument
        result = func(*args, **kwargs)

        end = time.time()

        # duration of the function
        dur = round(end - start, 7)

        # log
        with open(f'{paths["log_path"]}/process_time_log.csv',
                  mode='a') as file:

            writer = csv.writer(file)
            writer.writerow([date, dur, func.__name__])

        # checks if the function is to train or execute the classifier
        if (func.__name__ == 'train_classifier'
            or func.__name__ == 'execute_classifier'):
            return result, date, dur
        else:
            return result
    return timer


def choices_log(choices):
    """Records the choices made during the training of the machine learning
    algorithms.

    Parameters
    ----------
    choices: list
        Choices made during the training."""

    with open(f'{paths["log_path"]}/choices_log.csv', mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.strftime(datetime.now(),
                                           '%Y-%m-%d %H:%M:%S'), choices])


def clean_files(nfcapd_path, csv_path, execute_model=False):
    if not execute_model:
        # remove temporary files from nfcapd path
        os.system("rm {0}nfcapd*".format(nfcapd_path))
    else:
        os.system("rm {0}nfcapd.20*".format(nfcapd_path))
        os.system("mv {0}tmp_flows/* {0}raw_flows".format(csv_path))


def clean_objects(nfcapd_path, obj_path):
        os.system("rm {0}dt".format(obj_path))
        os.system("rm {0}ex".format(obj_path))



