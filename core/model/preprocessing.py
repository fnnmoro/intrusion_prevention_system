"""This module..."""
import ast
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (StandardScaler, MinMaxScaler,
                                   MaxAbsScaler, RobustScaler,
                                   QuantileTransformer, Normalizer)


class Formatter:
    """Formats the raw csv"""

    def __init__(self, flows):
        """Initializes the main variable"""

        self.flows = flows

    def format_flows(self, lbl_num=2, training_model=False):

        header = []
        for entry in self.flows:
            if not training_model:
                self.delete_features(entry)
                self.change_columns(entry)
                # checks if is the header
                if "ts" in entry[0]:
                    header.append(entry)
                else:
                    self.replace_missing_features(entry)
                    self.change_data_types(entry)
                    self.count_flag(entry)
                    entry.append(1)
                    entry.append(lbl_num)
            else:
                if "ts" in entry[0]:
                    header.append(entry)
                else:
                    self.change_data_types(entry, True)
        del self.flows[0]

        if not training_model:
            header[0][7] = "iflg"
            header[0].extend(["flw", "lbl"])

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
    def change_data_types(entry, training_model=False):
        """Changes the data type according to the type of the feature"""

        entry[0:2] = [datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
                      for i in entry[0:2]]
        entry[8:10] = [int(i) for i in entry[8:10]]
        entry[10] = round(float(entry[10]))
        entry[11:] = [int(i) for i in entry[11:]]

        if training_model:
            entry[7] = ast.literal_eval(entry[7])
        else:
            entry[6:8] = [i.lower() for i in entry[6:8]]

    @staticmethod
    def count_flag(entry):
        """Changes the flag feature by deleting the dots in the middle of
        the characters"""

        entry[7] = list(filter(lambda flg: flg != ".", entry[7]))

        # checks if the protocol that was used is tcp
        if entry[6] == "tcp":
            tmp = [0, 0, 0, 0, 0, 0]

            tmp[0] = entry[7].count('u')
            tmp[1] = entry[7].count('a')
            tmp[2] = entry[7].count('s')
            tmp[3] = entry[7].count('f')
            tmp[4] = entry[7].count('r')
            tmp[5] = entry[7].count('p')

            entry[7] = tmp
        else:
            entry[7] = [0]

    @staticmethod
    def replace_missing_features(entry):
        """Replaces the missing features for specific values"""
        replacement = {0:"0001-01-01 01:01:01", 1:"0001-01-01 01:01:01",
                       2:"00:00:00:00:00:00", 3:"00:00:00:00:00:00",
                       4:"000.000.000.000", 5:"000.000.000.000",
                       6:"nopr", 7:"......", 8:"0", 9:"0",
                       10:"0.0", 11:"0", 12:"0"}

        for idx, feature in enumerate(entry):
            # check if the feature are empty
            if feature == '':
                entry[idx] = replacement.get(idx)


class Modifier:
    def __init__(self, flows, header):
        self.flows = flows
        self.header = header

    def modify_flows(self, threshold, aggregate=False):
        if aggregate:
            self.aggregate_flows(threshold)
        self.create_features()

        return self.header, self.flows

    def aggregate_flows(self, threshold):
        """Aggregates the flows according to features of mac, ip and protocol"""
        tmp_flows = []

        # replaces sp and dp to isp and idp
        self.header[0][8] = "isp"
        self.header[0][9] = "idp"

        while len(self.flows) != 0:
            count = 1
            entry = self.flows.pop(0)

            # keeps only the ports with unique numbers
            sp = {entry[8]}
            dp = {entry[9]}
            # checks if there are more occurrences in relation to the
            # first one
            for tmp_idx, tmp_entry in enumerate(self.flows):
                if count < threshold:
                    rules2 = [entry[0].hour == tmp_entry[0].hour,
                              entry[0].minute == tmp_entry[0].minute,
                              entry[2:7] == tmp_entry[2:7]]
                    if all(rules2):
                        self.aggregate_features(entry, tmp_entry, sp, dp)
                        # marks the occurrences already aggregated
                        self.flows[tmp_idx] = [None]

                        count += 1
                else:
                    break
            # counts the quantity of ports with the same occurences
            entry[8] = len(sp)
            entry[9] = len(dp)
            entry[10] = entry[1].second - entry[0].second

            tmp_flows.append(entry)

            if count > 1:
                # filters only the entries of aggregate flows
                self.flows = list(filter(lambda entry: entry != [None], self.flows))

        self.flows = tmp_flows

    @staticmethod
    def aggregate_features(entry, tmp_entry, sp, dp):
        """Aggregates the features from the first occurrence with the another
        occurrence equal"""

        if entry[1] < tmp_entry[1]:
            entry[1] = tmp_entry[1]

        entry[7] = [x + y for x, y in zip(entry[7], tmp_entry[7])]
        sp.add(tmp_entry[8])
        dp.add(tmp_entry[9])
        entry[10] = entry[1] - entry[0]
        entry[11] += tmp_entry[11]
        entry[12] += tmp_entry[12]
        entry[13] += tmp_entry[13]

    def create_features(self):
        """Creates new features"""
        self.header[0][13:13] = ["bps", "bpp", "pps"]

        for entry in self.flows:
            # checks if the packet value isn't zero
            if entry[11] != 0:
                # bits per packet
                bpp = int(round(((8 * entry[12]) / entry[11]), 0))
            else:
                bpp = 0

            # checks if the time duration isn't zero
            if entry[10] > 0:
                # bits per second
                bps = int(round(((8 * entry[12]) / entry[10])))
                # packet per second
                pps = int(round(entry[11] / entry[10]))
            else:
                bps = 0
                pps = 0

            entry[13:13] = [bps, bpp, pps]


class Extractor:
    """Extracts the features and labels"""

    def __init__(self):
        """Initializes the main variables"""
        self.preprocessing = [None,
                              StandardScaler(),
                              MinMaxScaler(),
                              MaxAbsScaler(),
                              RobustScaler(),
                              QuantileTransformer(output_distribution='normal'),
                              Normalizer()]

        self.methods = ['normal', 'standard scaler',
                        'minmax scaler', 'maxabs scaler',
                        'robust scaler', 'quantile transformer',
                        'normalizer']

    def extract_features(self, header, flows, choices):
        """Extracts the features"""

        header_features = []
        features = []

        for entry in header:
            tmp = []
            for idx in choices:
               tmp.append(entry[idx])

            header_features.append(tmp)

        for entry in flows:
            tmp = []
            for idx in choices:
                tmp.append(entry[idx])

            features.append(tmp)

        return header_features, features

    def extract_labels(self, flows):
        """Extracts the labels"""

        labels = []

        for entry in flows:
            labels.append(entry[-1])

        return labels

    def transform(self, features, choice, execute_model=False):
        if choice != 0:
            if not execute_model:
                self.preprocessing = self.preprocessing[choice]
            std_features = self.preprocessing.fit_transform(features)

            return std_features
        return features

    def train_test_split(self, features, labels, test_size):
        dataset = train_test_split(features, labels, test_size=test_size,
                                   stratify=labels)

        return dataset