import sys
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


def print_flows(flows, header="", sample=-1):
    """Prints the flows"""

    count = 0

    if header != "":
        for entry in header:
            tmp = 0
            print("", end=' ')
            for features in entry:
                column = str(tmp) + ' ' + features
                print("{0:^30}".format(column), end=' ')
                tmp += 1
        print()

    for entry in flows:
        if count != sample:
            print(count, end=' ')
            for features in entry:
                print("{0:^30}".format(str(features)), end=' ')
        else:
            break
        count += 1
        print()
    print()


def export_flows(flows, dst_path, file_name, header ="", mode='w', sample=-1):
    """Exports the flows"""

    try:
        with open(dst_path + file_name, mode=mode) as file:
            count = 0

            csv_file = csv.writer(file)

            if header != "":
                for entry in header:
                    csv_file.writerow(entry)

            for entry in flows:
                if count != sample:
                    csv_file.writerow(entry)
                else:

                    break
                count += 1
    except FileNotFoundError as error:
        print(error, end="\n\n")


def record_datatime(dst_path=""):
    try:
        with open(dst_path, mode='a') as file:
            print(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), end="\n\n", file=file)
    except FileNotFoundError as error:
        print(error, end="\n\n")


def processing_time(start, end, name="", dst_path="", no_output=False):
    """Prints the processing time"""
    time = round(end - start, 7)
    if no_output == False:
        try:
            with open(dst_path, mode='a') as file:
                    print("{0} time: {1}".format(name, time), end="\n\n", file=file)
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


def evaluation_metrics(test_labels, pred, parm, information, dst_path, idx):
    """Prints the evaluation metrics for the machine learning algorithms"""
    try:
        with open(dst_path, mode='a') as file:
            csv_file = csv.writer(file)
            conf_matrix = confusion_matrix(test_labels, pred)

            information.extend([round(precision_score(test_labels, pred), 3),
                                round(recall_score(test_labels, pred), 3),
                                round(f1_score(test_labels, pred), 3),
                                conf_matrix[0][0], conf_matrix[0][1],
                                conf_matrix[1][0], conf_matrix[1][1],
                                parm])

            if idx == 0:
                csv_file.writerow(["datetime", "method", "duration", "precison", "recall", "f1-score",
                                   "nn", "na", "an", "aa", "parameters"])
            csv_file.writerow(information)

    except FileNotFoundError as error:
        print(error, end="\n\n")


def scatter_plot(features, labels, x_column, y_column, x_lbl="", y_lbl="", title=""):
    colors = ["gray" if lbl == 0 else "red" for lbl in labels]

    plt.scatter([entry[x_column] for entry in features], [entry[y_column] for entry in features],
                c=colors, alpha=0.5)

    n_flows = ptc.Patch(color='gray', label='normal flows')
    a_flows = ptc.Patch(color='red', label='anomalous flows')
    plt.legend(handles=[n_flows, a_flows])

    plt.xlabel(x_lbl)
    plt.ylabel(y_lbl)
    plt.title(title)

    plt.show()


def show_directory_content(content, path):
    print("\n {0}".format(path))
    print("{0:^7} {1:^7} {2:^30}".format("index", "type", "file"))

    count = 1
    # prints all the directories
    for file in sorted(content[1]):
        print("{0:^7} {1:^7} {2:^30}".format(count, "d", file))
        count += 1
    print()
    count = 1

    # prints all the files
    for file in sorted(content[2]):
        print("{0:^7} {1:^7} {2:^30}".format(count, "f", file))
        count += 1
