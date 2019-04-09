import ast
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (StandardScaler, MinMaxScaler,
                                   MaxAbsScaler, RobustScaler,
                                   QuantileTransformer, Normalizer)
from model.tools import process_time_log


class Formatter:
    """Formats the IP flows to be used by machine learning algorithms.

    The formatted IP flows can be used in the Modifier class to aggregate or
    created new features.

    Parameters
    ----------
    header: list
        Features description.
    flows: list
        IP flows.

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
        """Format the header.

        Returns
        -------
        list
            Formatted header."""

        self.delete_features(self.header)
        self.sort_features(self.header)

        return self.header

    @process_time_log
    def format_flows(self):
        """Formats the flows to be used in the machine learning algorithms.

        Returns
        -------
        list
            Formatted flows."""

        # deletes the summary lines
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
        """Deletes non-discriminative features.

        Parameters
        ----------
        entry: list
            IP flow entry."""

        # fwd and stos
        del entry[9:11]
        # from opkt to the end
        del entry[11:]

    @staticmethod
    def sort_features(entry):
        """Sorts the features in a specific order.

        Parameters
        ----------
        entry: list
            IP flow entry."""

        # updates existing entry with the new order
        entry[:] = [entry[idx] for idx in [0, 1, 3, 4, 7, 8, 5, 6, 2, 9, 10]]

    @staticmethod
    def replace_features(entry):
        """Replaces the missing features.

        Parameters
        ----------
        entry: list
            IP flow entry."""

        default_values = {0: '0001-01-01 01:01:01', 1: '0001-01-01 01:01:01',
                          2: '000.000.000.000', 3: '000.000.000.000',
                          4: 'nopr', 5: '......', 6: '0', 7: '0',
                          8: '0', 9: '0', 10: '0'}

        for idx, feature in enumerate(entry):
            # checks missing features
            if not feature:
                entry[idx] = default_values[idx]

    @staticmethod
    def convert_features(entry, train=False):
        """Converts the features to specific data types.

        Parameters
        ----------
        entry: list
            IP flow entry.
        train: bool
            Boolean value to flag if the program is in train mode."""

        # ts, te
        entry[0:2] = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
                      for i in entry[0:2]]
        # pr
        entry[4] = entry[4].lower()
        # sp, dp
        entry[6:8] = [int(i) for i in entry[6:8]]
        # td
        entry[8] = round(float(entry[8]))
        # ibyt to the end
        entry[9:] = [int(i) for i in entry[9:]]

        # checks if is in the train mode to convert properly
        if train:
            # flg
            entry[5] = ast.literal_eval(entry[5])
        else:
            entry[5] = entry[5].lower()

    @staticmethod
    def count_flags(entry):
        """Counts TCP flags.

        Parameters
        ----------
        entry: list
            IP flow entry."""

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
    """Extracts features from flows and split the dataset into appropriate
    sets to training the model.

    Attributes
    ----------
    features_idx: int
        Index used according the chosen dataset.
    selected_features: list
        List of all chosen features."""

    def __init__(self):
        self.features_idx = 8
        self.selected_features = list()

    @process_time_log
    def extract_features(self, flows):
        """Extracts features and labels from flows.

        Parameters
        ----------
        flows: list
            Formatted and modified flows.

        Returns
        -------
        list
            Features and labels to be split into appropriate sets."""

        features, labels = list(), list()

        for entry in flows:
            tmp = list()
            for idx in self.selected_features:
                tmp.append(entry[self.features_idx:][idx])
            features.append(tmp)
            labels.append(entry[-1])

        return features, labels

    @process_time_log
    def train_test_split(self, features, labels, test_size):
        """Splits the features and labels into training and test sets.

        Parameters
        ----------
        features: list
            Features of each flows.
        labels: list
            Labels of each flows.
        test_size: float
            Size of the test set.

        Returns
        -------
        list
            Dataset containing the training and test sets."""

        dataset = train_test_split(features, labels,
                                   test_size=test_size,
                                   random_state=13,
                                   stratify=labels)
        return dataset


class Preprocessor:
    """Preprocessing methods to be used in the detection instance.

    Attributes
    ----------
    preprocesses: dict
        Preprocessing methods instances."""

    methods = {'normal': None,
               'maxabs scaler': MaxAbsScaler(),
               'minmax scaler': MinMaxScaler(),
               'standard scaler': RobustScaler(),
               'robust scaler': StandardScaler(),
               'normalizer': Normalizer(),
               'quantile transformer': QuantileTransformer(
                                            output_distribution='normal')}
