"""This module..."""

import os
import csv
import datetime
import subprocess
import numpy as np
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import SGDClassifier, PassiveAggressiveClassifier, Perceptron
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn import preprocessing


class Gatherer:
    """Gathering the raw flows"""
    def __init__(self, pcap_path="", nfcapd_path="", csv_path=""):
        self.pcap_path = pcap_path
        self.nfcapd_path = nfcapd_path
        self.csv_path = csv_path

    @staticmethod
    def directory_content(path):
        try:
            proceed = 1
            new_path = path
            old_path = []

            # loop to explore the directories
            while proceed == 1:
                count = 0

                # loop to list the content of the directories
                for content in os.walk(new_path, onerror=True):
                    print("\n {0}".format(new_path))
                    print("{0:^7} {1:^30}".format("index", "file"))

                    # checks if the directory is empty
                    if content[1] != [] or content[2] != []:
                        # prints all the directories
                        for file in sorted(content[1]):
                            print("{0:^7} {1:^30}".format(count, file))
                            count += 1
                        print()
                        count = 0

                        # prints all the files
                        for file in sorted(content[2]):
                            print("{0:^7} {1:^30}".format(count, file))
                            count += 1

                        # select the current directory
                        idx = int(input("\nselect this directory: "))
                        proceed = 0

                        # if you do not select the directory and it's not empty
                        # it's possible to back to main or choose a directory
                        if idx != 1:
                            back_main = int(input("back to previous directory: "))

                            # if selected, return to the main path
                            if back_main == 1:
                                if old_path != []:
                                    new_path = old_path.pop(-1)
                            else:
                                idx = int(input("choose directory: "))
                                # stores the old path to can back
                                old_path.append(new_path)
                                # concatenates the select directory with the path
                                new_path += sorted(content[1])[idx] + "/"
                            proceed = 1

                    else:
                        print("\nthere isn't content inside {0}".format(new_path))
                        if old_path != []:
                            new_path = old_path.pop(-1)
                    break

            return new_path, sorted(content[2])
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

    def split_pcap(self, size=0):
        try:
            # avoids to split if there isn't necessary
            if size != 0:
                # gets the path and the list of files
                tmp_pcap_path, pcap_file = self.directory_content(self.pcap_path)

                # creates the split temporary folder
                if not os.path.exists(tmp_pcap_path + "split/"):
                    os.system("mkdir {0}split/".format(tmp_pcap_path))

                print()
                start_idx = int(input("choose the initial pcap file: "))
                final_idx = int(input("choose the final pcap file: "))
                print()

                # loop to split multiple pcap files
                for i in range(start_idx, final_idx+1):
                    file_name = pcap_file[i].split(".pcap")[0]

                    # executes tcpdump program to split the pcap files
                    subprocess.run("tcpdump -r {0}{1} -w {0}split/{2} -C {3}"
                                   .format(tmp_pcap_path, pcap_file[i], file_name, size), shell=True,
                                   check=True)

                    print()

                # renames all split pcap files
                for file in sorted(os.listdir(self.pcap_path)):
                    if file_name in file:
                        os.rename(self.pcap_path + file, "{0}{1}.pcap".format(self.pcap_path, file))
        except subprocess.CalledProcessError as error:
            print()
            print(error, end="\n\n")
        except ValueError as error:
            print()
            print(error, end="\n\n")
        except IndexError as error:
            print()
            print(error, end="\n\n")

    def convert_pcap_nfcapd(self, win_time=0):
        try:
            # gets the path and the list of files
            tmp_pcap_path, pcap_files = self.directory_content(self.pcap_path)

            # creates the nfcapd folder
            if not os.path.exists(self.nfcapd_path):
                os.system("mkdir {0}".format(self.nfcapd_path))

            print()
            start_idx = int(input("choose the initial pcap file: "))
            final_idx = int(input("choose the final pcap file: "))
            print()

            # loop to read the pcap files to convert to nfcapd files
            for i in range(start_idx, final_idx+1):
                print()
                print(pcap_files[i])
                subprocess.run("nfpcapd -t {0} -T 10,11,64 -r {1}{2} -l {3}"
                               .format(win_time, tmp_pcap_path, pcap_files[i], self.nfcapd_path), shell=True, check=True)
        except subprocess.CalledProcessError as error:
            print()
            print(error, end="\n\n")
        except ValueError as error:
            print()
            print(error, end="\n\n")
        except IndexError as error:
            print()
            print(error)

    def convert_nfcapd_csv(self):
        try:
            # gets the path and the list of files
            nfcapd_files = self.directory_content(self.nfcapd_path)[1]

            # creates the nfcapd folder
            if not os.path.exists(self.csv_path):
                os.system("mkdir {0}".format(self.csv_path))
                os.system("mkdir {0}raw_flows/".format(self.csv_path))
                os.system("mkdir {0}flows/".format(self.csv_path))

            print()
            start_idx = int(input("choose the initial nfcapd file: "))
            final_idx = int(input("choose the final nfcapd file: "))
            print()

            name = input("csv name: ")
            print()
            # time to complete the file name
            start_time = nfcapd_files[start_idx].split("nfcapd.")[1]
            final_time = nfcapd_files[final_idx].split("nfcapd.")[1]
            file_name = name + "_" + start_time + "-" + final_time + ".csv"

            # read the nfcapd files and convert to csv files
            subprocess.run("nfdump -O tstart -o csv -6 -R {0}{1}:{2} > {3}raw_flows/raw_{4}"
                           .format(self.nfcapd_path, nfcapd_files[start_idx], nfcapd_files[final_idx],
                                   self.csv_path, file_name), shell=True, check=True)
            return file_name
        except subprocess.CalledProcessError as error:
            print()
            print(error, end="\n\n")
        except ValueError as error:
            print()
            print(error, end="\n\n")
        except IndexError as error:
            print()
            print(error, end="\n\n")

    def open_csv(self, sample=-1):
        """Opens a CSV file containing raw flows"""
        try:
            csv_path, csv_files = self.directory_content(self.csv_path)

            print()
            idx = int(input("choose csv file: "))
            print()

            with open(csv_path + csv_files[idx], mode='r') as file:
                csv_file = csv.reader(file)
                flows = []
                count = 0

                for line in csv_file:
                    # checks if the core number has been reached
                    if count != sample:
                        # checks if is not the last line
                        if "Summary" not in line[0]:
                            flows.append(line)
                            count += 1
                        # break if the last line was found
                        else:
                            break
                    # break if the core was reached
                    else:
                        break
                return flows
        except IndexError as error:
            print()
            print(error, end="\n\n")

    def clean_nfcapd_files(self):
        # remove temporary files from nfcapd path
        os.system("rm {0}nfcapd*".format(self.nfcapd_path))


class Formatter:
    """Formats the raw csv"""

    def __init__(self, flows):
        """Initializes the main variable"""

        self.flows = flows

    def format_flows(self, train_model=False):
        """Formats the raw flows into flows to used in machine learning algorithms"""

        header = []
        for entry in self.flows:
            if train_model == False:
                self.delete_features(entry)
                self.change_columns(entry)
                # checks if is the header
                if "ts" in entry[0]:
                    header.append(entry)
                else:
                    self.replace_missing_features(entry)
                    self.change_data_types(entry)
                    self.format_flag(entry)
            else:
                if "ts" in entry[0]:
                    header.append(entry)
                else:
                    self.change_data_types(entry, train_model=True)
        del self.flows[0]

        return header, self.flows

    @staticmethod
    def delete_features(entry):
        """Deletes features that won't be used"""

        del entry[9:11]  # deletes fwd and stos
        del entry[11:25]  # deletes from opkt to dvln
        del entry[13:]  # deletes from idmc to the end

    @staticmethod
    def change_columns(entry):
        """Changes the columns in order to separate the features
        that will be used in the machine learning algorithms"""

        index_order = [0, 1, 11, 12, 3, 4, 7, 8, 5, 6, 2, 9, 10]
        # temporary store the entry with its new order
        tmp = [entry[idx] for idx in index_order]
        # replaces all features with new ones
        for idx, features in enumerate(tmp):
            entry[idx] = features

    @staticmethod
    def change_data_types(entry, train_model=False):
        """Changes the data type according to the type of the feature"""

        entry[0:2] = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in entry[0:2]]
        entry[6:8] = [i.lower() for i in entry[6:8]]
        entry[8:10] = [int(i) for i in entry[8:10]]
        entry[10] = round(float(entry[10]), 3)
        entry[11:13] = [int(i) for i in entry[11:13]]
        if train_model == True:
            entry[13:17] = [int(i) for i in entry[13:17]]

    @staticmethod
    def format_flag(entry):
        """Changes the flag feature by deleting the dots in the middle of
        the characters"""

        entry[7] = list(filter(lambda flg: flg != ".", entry[7]))

    @staticmethod
    def replace_missing_features(entry):
        """Replaces the missing features for specific values"""
        replacement = {0:"0001-01-01 01:01:01", 1:"0001-01-01 01:01:01", 2:"00:00:00:00:00:00",
                       3:"00:00:00:00:00:00", 4:"000.000.000.000", 5:"000.000.000.000", 6:"nopr",
                       7:"......", 8:"0", 9:"0", 10:"0.0", 11:"0", 12:"0"}

        for idx, feature in enumerate(entry):
            # check if the feature are empty
            if feature == '':
                entry[idx] = replacement.get(idx)


class Modifier:
    def __init__(self, flows, header):
        self.flows = flows
        self.header = header

    def modify_flows(self):
        # if self.aggregate is on, insert flw before lbl
        self.header[0].extend(["bps", "bpp", "pps", "lbl"])
        self.header[0][7] = "iflg"

        lbl_num = int(input("label number: "))
        print()

        for entry in self.flows:
            self.create_features(entry)
            #entry.append(1)
            entry.append(lbl_num)
            self.count_flags(entry)

        #self.aggregate_flows()

        return self.header, self.flows

    @staticmethod
    def create_features(entry):
        """Creates new features"""

        # checks if the packet value isn't zero
        if entry[11] != 0:
            # bits per packet
            bpp = int(round(((8 * entry[12]) / entry[11]), 0))
        else:
            bpp = 0
        # checks if the time duration isn't zero
        if entry[10] > 0:
            # bits per second
            bps = int(round(((8 * entry[12]) / entry[10]), 0))
            # packet per second
            pps = int(round(entry[11] / entry[10], 0))
        else:
            bps = 0
            pps = 0

        entry.extend([bps, bpp, pps])

    @staticmethod
    def count_flags(entry):
        """Counts the quantity of each TCP flags"""
        tmp = [0, 0, 0, 0, 0, 0]

        # checks if the protocol that was used is tcp
        if entry[6] == "tcp":
            tmp[0] = entry[7].count('u')
            tmp[1] = entry[7].count('a')
            tmp[2] = entry[7].count('s')
            tmp[3] = entry[7].count('f')
            tmp[4] = entry[7].count('r')
            tmp[5] = entry[7].count('p')

            entry[7] = tmp
        else:
            entry[7] = [0]

    def aggregate_flows(self):
        """Aggregates the flows according to features of mac, ip and protocol"""

        # replaces sp and dp to isp and idp
        self.header[0][8] = "isp"
        self.header[0][9] = "idp"

        # aggregates the flows entries in the first occurrence
        for idx, entry in enumerate(self.flows):
            # checks if the entry has already been aggregated
            if entry != [None]:
                # keeps only the ports with unique numbers
                sp = {entry[8]}
                dp = {entry[9]}
                # checks if there are more occurrences in relation to the first one
                for tmp_idx, tmp_entry in enumerate(self.flows):
                    # avoids aggregating the first occurrence twice
                    if tmp_idx > idx:
                        # checks if the mac, ip and protocol are equal in the occurrences
                        if entry[2:7] == tmp_entry[2:7]:
                            self.aggregate_features(entry, tmp_entry, sp, dp)
                            # marks the occurrences already aggregated
                            self.flows[tmp_idx] = [None]
                # counts the quantity of ports with the same occurences
                entry[8] = len(sp)
                entry[9] = len(dp)

        # filters only the entries of aggregate flows
        self.flows = list(filter(lambda entry: entry != [None], self.flows))

        return self.header, self.flows

    @staticmethod
    def aggregate_features(entry, tmp_entry, sp, dp):
        """Aggregates the features from the first occurrence with the another
        occurrence equal"""

        entry[1] = tmp_entry[1]
        entry[7] = [x + y for x, y in zip(entry[7], tmp_entry[7])]
        sp.add(tmp_entry[8])
        dp.add(tmp_entry[9])
        entry[10] = round(entry[10] + tmp_entry[10], 3)
        entry[11] += tmp_entry[11]
        entry[12] += tmp_entry[12]
        entry[13] += tmp_entry[13]
        entry[14] += tmp_entry[14]
        entry[15] += tmp_entry[15]
        entry[16] += tmp_entry[16]


class Extractor:
    """Extracts the features and labels"""

    def __init__(self, flows):
        """Initializes the main variables"""
        self.flows = flows

    def extract_features(self):
        """Extracts the features"""

        features = []

        for entry in self.flows:
            features.append(entry[10:16])

        return features

    def extract_labels(self):
        """Extracts the labels"""

        labels = []

        for entry in self.flows:
            labels.append(entry[-1])

        return labels

    def preprocessing_features(self, features):
        ppa = preprocessing.QuantileTransformer()
        std_features = ppa.fit_transform(features)

        return std_features

    def k_fold(self, n_splits, shuffle, features, labels):
        """Divides into many sets the features and labels to training and test"""
        kf = KFold(n_splits=n_splits, shuffle=shuffle)
        dataset = []

        for training_index, test_index in kf.split(features):
            training_features = [features[i] for i in training_index]
            test_features = [features[i] for i in test_index]
            training_labels = [labels[i] for i in training_index]
            test_labels = [labels[i] for i in test_index]

            dataset.append([training_features, test_features, training_labels, test_labels])

        return dataset


class Detector:
    """Detects anomalous flow using machine learning algorithms"""

    def __init__(self):
        """Initializes the main variables"""
        self.classifiers = []
        #self.online_classifiers = []

    def create_classifiers(self, param):
        self.classifiers.extend([DecisionTreeClassifier(), BernoulliNB(), GaussianNB(), MultinomialNB(),
                                 KNeighborsClassifier(), SVC(), SGDClassifier(), PassiveAggressiveClassifier(),
                                 Perceptron(), MLPClassifier()])

        """self.online_classifiers.extend([BernoulliNB(), GaussianNB(), MultinomialNB(), SGDClassifier(),
                                        PassiveAggressiveClassifier(), Perceptron(), MLPClassifier()])"""

        for i in range(len(self.classifiers)):
            self.classifiers[i] = GridSearchCV(self.classifiers[i], param[i])

    @staticmethod
    def define_parameters():
        dtr = {"criterion": ["gini", "entropy"], "splitter": ["best", "random"], "max_depth": [3, 6, 9],
               "min_samples_leaf": [1, 5, 10], "min_samples_split": [2, 5, 10]}

        bnb = {"alpha": [0.5, 1.0], "fit_prior": [True, False]}

        gnb = {}

        mnb = {"alpha": [0.5, 1.0], "fit_prior": [True, False]}

        knn = {"n_neighbors": [5, 10, 15], "weights": ["uniform", "distance"],
                     "algorithm": ["ball_tree", "kd_tree", "brute"], "leaf_size": [1, 15, 30]}

        svm = [{"kernel": ["linear"], "C": [0.01, 0.1, 1.0, 10.0]}, {"kernel": ["rbf", "poly", "sigmoid"],
                "C": [0.01, 0.1, 1.0, 10.0], "gamma": [0.01, 0.1, 1.0, 10.0]}]

        sgd = {"loss": ["hinge", "modified_huber", "perceptron"], "penalty": ["l1", "l2", "elasticnet"],
                     "max_iter": [np.ceil(10**6 / 60398), 50, 100], "alpha": [0.0001, 0.01, 0.1],
                     "learning_rate": ["constant", "optimal"], "eta0": [0.0, 1.0]}

        pag = {"C": [0.01, 0.1, 1.0, 10.0], "max_iter": [np.ceil(10 ** 6 / 60398), 50, 100],
               "loss": ["hinge", "squared_hinge"]}

        ppn = {"penalty": ["l1", "l2", "elasticnet"]}

        mlp = {"hidden_layer_sizes": [(5,2), (7, 5)], "activation": ["relu", "tanh", "logistic"],
               "solver": ["sgd", "lbfgs", "adam"], "alpha": [0.0001, 0.01, 0.1],
               "max_iter": [np.ceil(10**6 / 60398), 50, 100],
               "learning_rate": ["constant", "invscaling", "adaptive"]}

        #param = [dtr, bnb, gnb, mnb, knn, svm, sgd, pag, ppn, mlp]
        param = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

        return param

    def execute_classifiers(self, training_features, test_features, training_labels):
        pred = []
        param = []

        for clf in self.classifiers:
            clf.fit(training_features, training_labels)
            pred.append(clf.predict(test_features))
            param.append(clf.best_params_)

        """for on_clf in self.online_classifiers:
            on_clf.partial_fit(training_features, training_labels, classes=[0,1])
            pred.append(on_clf.predict(test_features))
            param.append({})"""

        return pred, param

    @staticmethod
    def find_patterns(features):
        pca = PCA(n_components=2)

        pattern = pca.fit_transform(features)

        return pattern

    def get_ma_models(self):
        return self.classifiers


class Mitigator:
    pass

