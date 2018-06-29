import os
import sys
import csv
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


def evaluation_metrics(pred, test_labels, param, method, num, dst_path, file_name):
    """Prints the evaluation metrics for the machine learning algorithms"""
    try:
        with open(dst_path + file_name, mode='a') as file:
            file.write("Test " + str(num) + "\n\n")

            print("[" + method + "]", end="\n\n", file=file)

            print("precion: ", round(precision_score(test_labels, pred, average="micro"), 3), file=file)
            print("recall: ", round(recall_score(test_labels, pred, average="micro"), 3), file=file)
            print("f1-score: ", round(f1_score(test_labels, pred, average="micro"), 3), file=file)
            conf_matrix = confusion_matrix(test_labels, pred)
            print(file=file)

            print("confusion_matrix", file=file)
            print("{0:^10}{1:^10}{2:^10}".format("", "normal", "anomalous"), file=file)
            for idx, line in enumerate(conf_matrix):
                if idx == 0:
                    print("{0:^10}".format("normal"), end='', file=file)
                else:
                    print("{0:^10}".format("anomalous"), end='', file=file)
                for results in line:
                    print("{0:^10}".format(results), end='', file=file)
                print(file=file)
            print(file=file)

            print("parameters: ", param, end="\n\n", file=file)
            print("----------", end="\n\n", file=file)

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