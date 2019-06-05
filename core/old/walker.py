import os


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
        print(f'{idx + 1} - {item}')

    return int(input('choose an option: '))

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
            # display contents
            self.list_contents()

            # menu options
            option = menu(['select this directory',
                           'choose another directory',
                           'back to previous directory',
                           'stop'])

            if option == 1:
                # chosen files
                print(end=f'{"-" * 10}\n')
                return self.get_files()
            elif option == 2:
                print(end=f'{"-" * 10}\n')
                self.next_dir()
                self.clean_contents()
                print(end=f'{"-" * 10}\n')
            elif option == 3:
                # doesn't allow to go back beyond the first absolute path
                if len(self.paths) > 1:
                    del self.paths[-1]
                    self.clean_contents()
            elif option == 4:
                return [list(), list()]
            else:
                print(end=f'{"-" * 10}\n')
                print('error: invalid option')

    def list_contents(self):
        """Displays the directories contents."""

        print('choose files', end=f'\n{"-" * 10}\n')
        # header
        print(f'{self.paths[-1]}', end=f'\n{"-" * 10}\n')
        print(f'{"index":^7} {"type":^7} {"content":^30}')

        # lists the directory content
        for idx, content in enumerate(sorted(os.listdir(self.paths[-1]))):
            # separates directories from files
            if os.path.isfile(f'{self.paths[-1]}{content}'):
                content_type = 'f'
                self.files[idx] = content
            else:
                content_type = 'd'
                self.dir[idx] = content

            print(f'{idx+1:^7} {content_type:^7} {content:^30}')
        print(end=f'{"-" * 10}\n')

    def get_files(self):
        """Gets the chosen files.

        Returns
        -------
        list
            Chosen files and the corresponding path."""

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
            self.paths.append(self.paths[-1]
                              +self.dir[int(input('choose the directory: '))
                                        -1])
        except ValueError:
            print(end=f'{"-" * 10}\n')
            print('error: invalid value')
        except KeyError:
            print(end=f'{"-" * 10}\n')
            print('error: invalid index')

    def clean_contents(self):
        """Cleans the current contents"""

        self.dir, self.files = dict(), dict()


def get_files(path):
    dirs = list()
    files = list()

    # lists the directory content
    for content in sorted(os.listdir(path)):
        # gets the directories
        if os.path.isdir(f'{path}{content}'):
            dirs.append(content)
        # gets the files
        else:
            files.append(content)

    return dirs, files
