import csv
import logging
import os
import time
from datetime import datetime
from pytz import timezone

from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score,
                             confusion_matrix)

from app.paths import paths


logger = logging.getLogger('tools')


def make_directory(path, directory):
    """Creates a directory, if it not exists.

    Parameters
    ----------
    path: str
        Absolute path."""

    count = 0
    while True:
        # new directory based on count value.
        new_directory = f'{directory}{count}/'
        if not os.path.exists(f'{path}{new_directory}'):
            os.system(f'mkdir {path}{new_directory}')

            return new_directory
        count += 1


def evaluation_metrics(test_labels, pred):
    """Computes the evaluation metrics for a given prediction.

    Parameters
    ----------
    test_labels: list
        Test labels that represent the correct answer for the predictions.
    pred: list
        Prediction made by a machine learning model."""

    tn, fp, fn, tp = confusion_matrix(test_labels, pred).ravel()

    outcome = {
        'accuracy': round(accuracy_score(test_labels, pred), 5),
        'precision': round(precision_score(test_labels, pred), 5),
        'recall': round(recall_score(test_labels, pred), 5),
        'f1_score': round(f1_score(test_labels, pred), 5),
        'tn': int(tn),
        'fp': int(fp),
        'fn': int(fn),
        'tp': int(tp)
    }

    return outcome


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

        writer.writerow(header)
        for entry in flows:
            writer.writerow(entry)


def process_time_log(func):
    """Decorator to record the time of a function.

    Parameters
    ----------
    func: func
        Function to calculate the processing time.

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

        date = datetime.now(timezone('America/Sao_Paulo'))
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = round(end - start, 7)

        logger.info(f'{func.__name__} duration: {duration}')

        if func.__name__ == 'train' or func.__name__ == 'test':
            return result, date, duration
        else:
            return result

    return timer


def get_content(path):
    """Gets the content of a directory.

    Parameters
    ----------
    path: str
        The absolute path of a directory."""

    directory = list()
    files = list()

    # listing directory content.
    for content in sorted(os.listdir(path)):
        if os.path.isdir(f'{path}{content}'):
            directory.append(content)
        else:
            files.append(content)

    return directory, files


def clean_files(path, file):
    """Cleans the files of a directory.

    Parameters
    ----------
    path: str
        The absolute path of a directory.
    file: str
        File name to be cleaned."""

    os.system(f'rm {path}{file}')
