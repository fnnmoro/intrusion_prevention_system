import os
import sys
from datetime import datetime
from view import show_directory_content


def menu(choices):
    for idx, item in enumerate(choices):
        print("{0} - {1}".format(idx+1, item))

    choice = int(input("choose an option: "))

    return choice


def check_path_exist(pcap_path, nfcapd_path, csv_path):
    if not os.path.exists(pcap_path):
        os.system("mkdir {0}".format(pcap_path))

    if not os.path.exists(nfcapd_path):
        os.system("mkdir {0}".format(nfcapd_path))

    if not os.path.exists(csv_path):
        os.system("mkdir {0}".format(csv_path))
        os.system("mkdir {0}flows/".format(csv_path))
        os.system("mkdir {0}raw_flows/".format(csv_path))
        os.system("mkdir {0}tmp_flows/".format(csv_path))


def directory_content(path, execute_model=False):
    try:
        path = [path]
        content = []

        option = 0
        # loop to explore the directories
        while option != 4:
            content = list(os.walk(path[-1]))[0]

            if execute_model == False:
                if content[1] != [] or content[2] != []:
                    show_directory_content(content, path[-1])

                    print()
                    option = menu(["select this directory",
                                   "choose another directory",
                                   "back to previous directory",
                                   "stop"])

                    if option == 1:
                        break
                    elif option == 2:
                        idx = int(input("directory index: "))
                        path.append("{0}{1}/".format(path[-1],
                                                     sorted(content[1])[idx-1]))
                    elif option == 3:
                        if path != []:
                            del path[-1]
                    elif option == 4:
                        break
                    else:
                        print("invalid option")
                else:
                    print("\nthere isn't content")
                    if path != []:
                        del path[-1]

        return path[-1], sorted(content[2])
    except FileNotFoundError as error:
        print()
        print(error, end="\n\n")
    except TypeError as error:
        print()
        print(error, end="\n\n")
    except IndexError as error:
        print()
        print(error, end="\n\n")
    except ValueError as error:
        print()
        print(error, end="\n\n")


def clean_files(nfcapd_path, csv_path, execute_model=False):
    if execute_model == False:
        # remove temporary files from nfcapd path
        os.system("rm {0}nfcapd*".format(nfcapd_path))
    else:
        os.system("rm {0}nfcapd.20*".format(nfcapd_path))
        os.system("mv {0}tmp_flows/* {0}raw_flows".format(csv_path))


def record_datatime(dst_path=""):
    try:
        with open(dst_path, mode='a') as file:
            print(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
                  end="\n\n", file=file)
    except FileNotFoundError as error:
        print(error, end="\n\n")


def processing_time(start, end, name="", dst_path="", no_output=False):
    """Prints the processing time"""
    time = round(end - start, 7)
    if no_output == False:
        try:
            with open(dst_path, mode='a') as file:
                    print("{0} time: {1}".format(name, time),
                          end="\n\n", file=file)
        except FileNotFoundError as error:
            print(error, end="\n\n")
    else:
        return time


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
