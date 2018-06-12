import os
import sys
import csv
import matplotlib.pyplot as plt
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
    except FileNotFoundError:
        print("File not found.", end="\n\n")


def processing_time(start, end, name):
    """Prints the processing time"""

    print("{0} time: {1}".format(name, round(end - start, 7)))


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


def evaluation_metrics(pred, test_labels, name):
    """Prints the evaluation metrics for the machine learning algorithms"""

    print(name)
    print("precion: ", round(precision_score(test_labels, pred, average="micro"), 3))
    print("recall: ", round(recall_score(test_labels, pred, average="micro"), 3))
    print("f1-score: ", round(f1_score(test_labels, pred, average="micro"), 3))
    conf_matrix = confusion_matrix(test_labels, pred)
    print()

    print("confusion_matrix")
    print("{0:^10}{1:^10}{2:^10}".format("", "normal", "anomalous"))
    for idx, line in enumerate(conf_matrix):
        if idx == 0:
            print("{0:^10}".format("normal"), end='')
        else:
            print("{0:^10}".format("anomalous"), end='')
        for results in line:
            print("{0:^10}".format(results), end='')
        print()
    print()


def scatter_plot(flows, xfeature, yfeature, xlabel="", ylabel="", title=""):
    plt.scatter([entry[xfeature] for entry in flows], [entry[yfeature] for entry in flows], c="red")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.show()