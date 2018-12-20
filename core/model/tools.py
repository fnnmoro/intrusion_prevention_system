import os
import sys
import csv
import time
from datetime import datetime


def menu(options):
    """Generates the menu options.

    Parameters
    ----------
    options: list
        Menu options to be chosen.
        
    Returns
    -------
    int
        Chosen option."""

    for idx, item in enumerate(options):
        print(f'{idx+1} - {item}')

    return int(input('choose an option: '))


def make_dir(path):
    """Creates a directory, if it not exists.

    Parameters
    ----------
    path: str
        Absolute path."""

    if not os.path.exists(path):
        os.system(f'mkdir {path}')


class DirectoryContents:
    """Searches for contents in a chosen directory.

    Parameters
    ----------
    path: str
        Absolute path.

    Attributes
    ----------
    path: list
        All absolute path.
    dir: dict
        All directories in the current path.
    files: dict
        All files in the current path."""

    def __init__(self, path):
        self.paths = [path]
        self.dir = dict()
        self.files = dict()

    def choose_files(self):
        """Chooses the files in a directory.

        Returns
        -------
        list
            Chosen files and the corresponding path."""

        option = 0

        while option != 4:
            # display contentes
            self.list_contents()

            print(end=f'{"-" * len(self.paths[-1])}\n')

            # menu options
            option = menu(['select this directory',
                           'choose another directory',
                           'back to previous directory',
                           'stop'])

            if option == 1:
                # chosen files
                return self.get_files()
            elif option == 2:
                self.next_dir()
                self.clean_contents()
            elif option == 3:
                # doesn't allow to go back beyond the first absolute path
                if len(self.paths) > 1:
                    del self.paths[-1]
                    self.clean_contents()
            elif option == 4:
                return [list(), list()]
            else:
                print(end=f'{"-" * len(self.paths[-1])}\n')
                print('error: invalid option')

    def list_contents(self):
        """Displays the directories contents."""

        print(end=f'{"-" * len(self.paths[-1])}\n')
        print('choose files')
        print(end=f'{"-" * len(self.paths[-1])}\n')
        # header
        print(f'{self.paths[-1]}', end=f'\n{"-" * len(self.paths[-1])}\n')
        print(f'{"index":^7} {"type":^7} {"content":^30}')

        # lists the directory content
        for idx, content in enumerate(sorted(os.listdir(self.paths[-1]))):
            # separates directories from files
            if os.path.isfile(self.paths[-1] + '/' + content):
                content_type = 'f'
                self.files[idx] = content
            else:
                content_type = 'd'
                self.dir[idx] = content

            print(f'{idx+1:^7} {content_type:^7} {content:^30}')

    def get_files(self):
        """Gets the chosen files.

        Returns
        -------
        list
            Chosen files and the corresponding path."""

        print(end=f'{"-" * len(self.paths[-1])}\n')

        return [self.paths[-1],
                list(self.files.values())
                [int(input('choose the initial file: '))-1:
                 int(input('choose the final file: '))]]

    def next_dir(self):
        """Goes to next selected directory.

        Raises
        -------
        ValueError
            Entered a value that is not a valid number.
        KeyError
            Entered a invalid index key."""

        try:
            print(end=f'{"-" * len(self.paths[-1])}\n')

            self.paths.append(self.paths[-1]
                              +'/'
                              +self.dir[int(input('choose the directory: '))
                                        -1])
        except ValueError:
            print(end=f'{"-" * len(self.paths[-1])}\n')
            print('error: invalid value')
        except KeyError:
            print(end=f'{"-" * len(self.paths[-1])}\n')
            print('error: invalid index')

    def clean_contents(self):
        """Cleans the current contents"""

        self.dir, self.files = dict(), dict()


def clean_tmp_files(nfcapd_path, csv_path, execute_model=False):
    if not execute_model:
        # remove temporary files from nfcapd path
        os.system("rm {0}nfcapd*".format(nfcapd_path))
    else:
        os.system("rm {0}nfcapd.20*".format(nfcapd_path))
        os.system("mv {0}tmp_flows/* {0}raw_flows".format(csv_path))

def clean_files(nfcapd_path, obj_path):
        os.system("rm {0}nfcapd.*".format(nfcapd_path))
        os.system("rm {0}dt".format(obj_path))
        os.system("rm {0}ex".format(obj_path))

def record_datatime(dst_path=""):
    try:
        with open(dst_path, mode='a') as file:
            print(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
                  end="\n\n", file=file)
    except FileNotFoundError as error:
        print(error, end="\n\n")


def processing_time_log(func):
    def timer(*args, **kwargs):
        date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        start = time.time()

        result = func(*args, **kwargs)

        end = time.time()
        dur = round(end - start, 7)

        try:
            with open('/home/flmoro/bsi16/research_project/codes/log/'
                      'processing_time_log.csv',
                      mode='a') as file:

                csv_file = csv.writer(file)
                csv_file.writerow([date, dur, func.__name__])
        except FileNotFoundError as error:
            print(error, end="\n\n")

        if func.__name__ == 'training_classifiers' \
                or func.__name__ == 'execute_classifiers':
            return result, date, dur
        else:
            return result
    return timer


def save_choices_log(choices, log_path):
    try:
        with open(log_path + 'save_choices_log.csv', mode='a') as file:

            csv_file = csv.writer(file)
            csv_file.writerow([datetime.strftime(datetime.now(),
                                                 "%Y-%m-%d %H:%M:%S"),
                               choices])
    except FileNotFoundError as error:
        print(error, end="\n\n")


def memory_size(object, name):
    """Prints the memory size of the object"""

    b = sys.getsizeof(object)

    print("{0} size: ".format(name), end=' ')

    if b >= 1073741824:
        gb = round(b / (1024 ** 3), 7)
        print("{0} GB".format(gb))
    elif b >= 1048576:
        mb = round(b / (1024 ** 2), 7)
        print("{0} MB".format(mb))
    elif b >= 1024:
        kb = round(b / 1024, 7)
        print("{0} KB".format(kb))
    else:
        print("{0} B".format(b))
