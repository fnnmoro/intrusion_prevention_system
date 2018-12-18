import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)
from sklearn.decomposition import PCA


def print_flows(flows, header="", sample=-1):
    """Prints the flows"""

    count = 0

    if header != "":
        for entry in header:
            tmp = 0
            print("", end=' ')
            for features in entry:
                column = str(tmp) + ' ' + features
                print("{0:^20}".format(column), end=' ')
                tmp += 1
        print()

    for entry in flows:
        if count != sample:
            print(count, end=' ')
            for features in entry:
                print("{0:^20}".format(str(features)), end=' ')
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


def evaluation_metrics(test_labels, param, pred, information, dst_path, idx):
    """Prints the evaluation metrics for the machine learning algorithms"""
    try:
        with open(dst_path, mode='a') as file:
            csv_file = csv.writer(file)
            conf_matrix = confusion_matrix(test_labels, pred)

            information.extend([round(accuracy_score(test_labels, pred), 5),
                                round(precision_score(test_labels, pred), 5),
                                round(recall_score(test_labels, pred), 5),
                                round(f1_score(test_labels, pred), 5),
                                conf_matrix[0][0], conf_matrix[0][1],
                                conf_matrix[1][0], conf_matrix[1][1],
                                param])

            if idx == 0:
                csv_file.writerow(["train_datetime", "test_datetime",
                                   "train_duration", "test_duration", "method",
                                   "accuracy", "precison", "recall", "f1-score",
                                   "tn", "fp", "fn", "tp",
                                   "parameters"])
            csv_file.writerow(information)

        return information

    except FileNotFoundError as error:
        print(error, end="\n\n")


def scatter_plot(features, labels, x_column, y_column, x_lbl, y_lbl):
    colors = ["gray" if lbl == 0 else "red" for lbl in labels]

    plt.scatter([entry[x_column] for entry in features],
                [entry[y_column] for entry in features],
                c=colors, alpha=0.5)

    n_flows = ptc.Patch(color='gray', label='normal flows')
    a_flows = ptc.Patch(color='red', label='anomalous flows')
    plt.legend(handles=[n_flows, a_flows])

    plt.xlabel(x_lbl)
    plt.ylabel(y_lbl)

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


def checkpoint(point, log_path):
    with open(log_path, 'a') as log:
        csv_file = csv.writer(log)

        if log.tell() == 0:
            csv_file.writerow(["date", "point"])

        csv_file.writerow([datetime.strftime(datetime.now(),
                                             "%Y-%m-%d %H:%M:%S"),
                           point])

def find_patterns(features):
    pca = PCA(n_components=2)

    pattern = pca.fit_transform(features)

    return pattern