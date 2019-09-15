import logging
import os
import time
from datetime import datetime
from pytz import timezone

from app.paths import paths


logger = logging.getLogger('util')


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


def timing(func):
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

        if func.__name__ != 'test': 
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
