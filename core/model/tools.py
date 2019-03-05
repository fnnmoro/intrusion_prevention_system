import os
import csv
import time
from datetime import datetime
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score,
                             confusion_matrix)

def make_dir(path):
    """Creates a directory, if it not exists.

    Parameters
    ----------
    path: str
        Absolute path."""

    if not os.path.exists(path):
        os.system(f'mkdir {path}')


def evaluation_metrics(test_labels, pred):
    conf_matrix = confusion_matrix(test_labels, pred)

    results = [round(accuracy_score(test_labels, pred), 5),
               round(precision_score(test_labels, pred), 5),
               round(recall_score(test_labels, pred), 5),
               round(f1_score(test_labels, pred), 5),
               conf_matrix[0][0], conf_matrix[0][1],
               conf_matrix[1][0], conf_matrix[1][1]]

    return results


def export_flows_csv(header, flows, dst_path, file_name):
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

    with open(f'{dst_path}{file_name}', mode='a') as file:
        writer = csv.writer(file)

        # writes header once when merge flows
        if not os.stat(f'{dst_path}{file_name}').st_size:
            writer.writerow(header)

        for entry in flows:
            writer.writerow(entry)


def export_results_csv(results, text, dst_path, file_name):
    with open(f'{dst_path}{file_name}', mode='a') as file:
        writer = csv.writer(file)

        if not os.stat(f'{dst_path}{file_name}').st_size:
            writer.writerow(text)

        writer.writerow(results)


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
        with open('/home/flmoro/bsi16/research_project/anomaly_detection/'
                  'codes/triple_m_ads/log/process_time_log.csv',
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


def clean_files(paths, files):
    for path, file in zip(paths, files):
        os.system(f'rm {path}{file}')
