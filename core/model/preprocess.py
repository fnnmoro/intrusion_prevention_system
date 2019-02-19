import ast
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (StandardScaler, MinMaxScaler,
                                   MaxAbsScaler, RobustScaler,
                                   QuantileTransformer, Normalizer)
from model.tools import process_time_log


class Formatter:
    """Formats the raw flows to be used by machine learning algorithms.

    Parameters
    ----------
    header: list
        Features description.
    flows: list
        Raw flows.

    Attributes
    ----------
    header: list
        Formatted features description.
    flows: list
        Formatted flows."""

    def __init__(self, header, flows):
        self.header = header
        self.flows = flows

    @process_time_log
    def format_header(self):
        """Formats the header with specific features and order.

        Returns
        -------
        list
            Formatted header."""

        self.delete_features(self.header)
        self.sort_features(self.header)

        return self.header

    @process_time_log
    def format_flows(self):
        """Formats the flows with specific features, order and replace missing
        features.

        Returns
        -------
        list
            Formatted flows."""

        # summary
        del self.flows[-3:]

        for entry in self.flows:
            self.delete_features(entry)
            self.sort_features(entry)
            self.replace_features(entry)
            self.convert_features(entry)
            self.count_flags(entry)

        return self.flows

    @staticmethod
    def delete_features(entry):
        """Deletes non-significant features.

        Parameters
        ----------
        entry: list
            Flow entry."""

        del entry[9:11]  # fwd and stos
        del entry[11:]  # from opkt to the end

    @staticmethod
    def sort_features(entry):
        """Sorts the features in a specific order.

        Parameters
        ----------
        entry: list
            Flow entry."""

        # entry with the new order
        tmp = [entry[idx] for idx in [0, 1, 3, 4, 7, 8, 5, 6, 2, 9, 10]]

        # updates each element of the existing entry
        for idx, feature in enumerate(tmp):
            entry[idx] = feature

    @staticmethod
    def replace_features(entry):
        """Replaces the missing features.

        Parameters
        ----------
        entry: list
            Flow entry."""

        # default values
        missing = {0: '0001-01-01 01:01:01', 1: '0001-01-01 01:01:01',
                   2: '000.000.000.000', 3: '000.000.000.000',
                   4: 'nopr', 5: '......', 6: '0', 7: '0',
                   8: '0.0', 9: '0', 10: '0'}

        for idx, feature in enumerate(entry):
            # checks missing features
            if not feature:
                entry[idx] = missing[idx]

    @staticmethod
    def convert_features(entry, train=False):
        """Converts the features to specific data types.

        Parameters
        ----------
        entry: list
            Flow entry.
        train: bool
            Boolean value to flag if the program is in train mode"""

        entry[0:2] = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
                      for i in entry[0:2]]  # ts, te
        entry[4] = entry[4].lower()  # pr
        entry[6:8] = [int(i) for i in entry[6:8]]  # sp, dp
        entry[8] = round(float(entry[8]))  # td
        entry[9:] = [int(i) for i in entry[9:]]  # ibyt to the end

        if train:
            entry[5] = ast.literal_eval(entry[5])  # flg
        else:
            entry[5] = entry[5].lower()

    @staticmethod
    def count_flags(entry):
        """Counts TCP flags.

        Parameters
        ----------
        entry: list
            Flow entry."""

        # checks if is the tcp protocol
        if entry[4] == 'tcp':
            # flags order
            flags = ['u', 'a', 's', 'f', 'r', 'p']

            # filters only the flags
            entry[5] = [flag for flag in entry[5] if flag != '.']
            # creates a new list with the flags order and the count of them
            entry[5] = [entry[5].count(flag) for flag in flags]
        else:
            entry[5] = [0]


class Modifier:
    """Modifies the formatted flows to create more discriminating features.

    Parameters
    ----------
    header: list
        Formatted features description.
    flows: list
        Formatted flows.

    Attributes
    ----------
    header: list
        Modified features description.
    flows: list
        Modified flows."""

    def __init__(self, flows, header):
        self.flows = flows
        self.header = header

    @process_time_log
    def aggregate_flows(self, threshold):
        """Aggregates formatted flows.

        Parameters
        ----------
        threshold: int
            Aggregation limit to prevent that the anomalous flows becoming
            just one entry.

        Returns
        -------
        list
            Modified header and flows"""

        # temporary aggregated flows
        tmp_flows = list()

        while self.flows:
            # compares the value with the defined threshold
            count = 1

            # separates the first entry that will be matched
            entry = self.flows.pop(0)

            # keeps only the ports with unique numbers
            sp = {entry[6]}
            dp = {entry[7]}

            # compares the first entry with the rest of the flows
            for tmp_idx, tmp_entry in enumerate(self.flows):
                # checks if the threshold was reached
                if count < threshold:
                    # default rules
                    rules = [entry[0].hour == tmp_entry[0].hour,
                             entry[0].minute == tmp_entry[0].minute,
                             entry[2:5] == tmp_entry[2:5]]

                    # searches for matching entry
                    if all(rules):
                        self.aggregate_features(entry, tmp_entry)
                        sp.add(tmp_entry[6])
                        dp.add(tmp_entry[7])

                        # marks the aggregated entry
                        self.flows[tmp_idx] = [None]
                        count += 1
                else:
                    break

            # counts the quantity of ports
            entry[6] = len(sp)
            entry[7] = len(dp)
            # time duration
            entry[8] = entry[1].second - entry[0].second
            # number of aggregated flows
            entry.append(count)

            tmp_flows.append(entry)

            # checks if aggregation happened
            if count > 1:
                # filters only the aggregated entries
                self.flows = [entry for entry in self.flows if entry != [None]]

        self.flows = tmp_flows
        self.header.append('flw')

        return self.header, self.flows

    @staticmethod
    def aggregate_features(entry, tmp_entry):
        """Aggregates features.

        Parameters
        ----------
        entry: list
            Aggregated flow entry.
        tmp_entry: list
            Flow entry to aggregate."""

        # important conditional because some entries are out of order
        if entry[1] < tmp_entry[1]:
            entry[1] = tmp_entry[1]  # te
        entry[5] = [x + y for x, y in zip(entry[5], tmp_entry[5])]  # flg
        entry[8] = entry[1] - entry[0]  # td
        entry[9] += tmp_entry[9]  # ibyt
        entry[10] += tmp_entry[10]  # ipkt

    @process_time_log
    def create_features(self, label):
        """Creates new features.

        Parameters
        ----------
        label: int
            Class of each entry."""

        for entry in self.flows:
            # default value
            bps, bpp, pps = [0, 0, 0]

            # checks if the time duration isn't zero
            if entry[8]:
                # bytes per second
                bps = int(round(entry[10] / entry[8]))
                # packet per second
                pps = int(round(entry[9] / entry[8]))

            # checks if the packet value isn't zero
            if entry[9]:
                # bytes per packet
                bpp = int(round(entry[10] / entry[9]))

            entry[11:11] = [bps, bpp, pps]
            entry.append(label)

        self.header[11:11] = ['bps', 'bpp', 'pps']
        self.header.append('lbl')

        return self.header, self.flows


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

        self.preprocessing_name = ['normal', 'standard scaler',
                                   'minmax scaler', 'maxabs scaler',
                                   'robust scaler', 'quantile transformer',
                                   'normalizer']

        self.features_header = ['source ports', 'destination ports', 'duration',
                         'packets', 'bytes', 'bits per second',
                         'bits per packets', 'packtes per second', 'flows']

    @process_time_log
    def extract_features(self, flows, options):
        """Extracts the features"""

        features, labels = list(), list()

        for entry in flows:
            tmp = list()
            for idx in options:
                tmp.append(entry[idx])

            features.append(tmp)
            labels.append(entry[-1])

        return features, labels


    def choose_preprocessing(self, choice, execute_model=False):
        if not execute_model:
            self.preprocessing_name = self.preprocessing_name[choice]
            self.preprocessing = self.preprocessing[choice]

    def choose_features(self, dataset_type):
        if dataset_type == 0:
            del self.features_header[0:2]
            del self.features_header[-1]


    @process_time_log
    def transform(self, train_features, test_features):
        scl_train = self.preprocessing.fit_transform(train_features)
        scl_test = self.preprocessing.transform(test_features)

        return scl_train, scl_test


    @process_time_log
    def train_test_split(self, features, labels, test_size):
        dataset = train_test_split(features, labels,
                                   test_size=test_size,
                                   random_state=13,
                                   stratify=labels)
        return dataset
