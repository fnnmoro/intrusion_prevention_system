import ast
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (StandardScaler, MinMaxScaler,
                                   MaxAbsScaler, RobustScaler,
                                   QuantileTransformer, Normalizer)

from app.core.tools import process_time_log


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
    self.header: list
        Formatted features description.
    self.flows: list
        Formatted IP flows."""

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
        """Formats the flows to be used by the machine learning algorithms.

        Returns
        -------
        list
            Formatted IP flows."""

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
            Value to flag if the program is in train mode."""

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
    """Modifies the formatted IP flows to aggregate and create more
    discriminating features to be used by the machine learning algorithms.

    Parameters
    ----------
    header: list
        Formatted features description.
    flows: list
        Formatted IP flows.

    Attributes
    ----------
    self.header: list
        Modified features description.
    self.flows: list
        Modified IP flows."""

    def __init__(self, header, flows):
        self.header = header
        self.flows = flows

    @process_time_log
    def aggregate_flows(self, threshold):
        """Aggregates formatted IP flows according to a established threshold.

        The flows are aggregated considering the same start hour and minute,
        source address, destination address and protocol.

        The threshold is useful when the flows to be aggregate are anomalous,
        like a DoS attack.

        Parameters
        ----------
        threshold: int
            Aggregation threshold to prevent that mulitple entries become just
            one.

        Returns
        -------
        self.header: list
            Modified features description.
        self.flows: list
            Modified IP flows."""

        # aggregated flows
        aggregated_flows = list()

        while self.flows:
            # separates the first flow that will be matched against the others
            base_entry = self.flows.pop(0)

            # keeps only the unique ports
            sp = {base_entry[6]}
            dp = {base_entry[7]}

            # compares the value with the established threshold
            # 1 is used instead of 0 because a flow is separated first
            count = 1
            # compares the first flows with the rest of the flows
            for idx, entry in enumerate(self.flows):
                # checks if the threshold was reached
                if count < threshold:
                    # default rules for aggregation
                    rules = [base_entry[0].hour == entry[0].hour,
                             base_entry[0].minute == entry[0].minute,
                             base_entry[2:5] == entry[2:5]]

                    if all(rules):
                        self.aggregate_features(base_entry, entry)
                        sp.add(entry[6])
                        dp.add(entry[7])

                        # marks the flow that was aggregated
                        self.flows[idx] = [None]
                        count += 1
                else:
                    break

            # counts the quantity of unique ports
            base_entry[6] = len(sp)
            base_entry[7] = len(dp)
            # time duration recalculed
            base_entry[8] = base_entry[1].second - base_entry[0].second
            # number of aggregated flows
            base_entry.append(count)
            aggregated_flows.append(base_entry)

            # checks if aggregation happened
            if count > 1:
                # filters only the not aggregated flows
                self.flows = [entry for entry in self.flows if entry != [None]]

        self.flows = aggregated_flows
        self.header.append('flw')

        return self.header, self.flows

    @staticmethod
    def aggregate_features(base_entry, entry):
        """Aggregates features of the current entry in the base entry.

        Parameters
        ----------
        base_entry: list
            Aggregated entry.
        entry: list
            Current entry to aggregate."""

        # important conditional because some entries are out of order
        if base_entry[1] < entry[1]:
            # te
            base_entry[1] = entry[1]
        # flg
        base_entry[5] = [x + y for x, y in zip(base_entry[5], entry[5])]
        # td
        base_entry[8] = base_entry[1] - base_entry[0]
        # byt
        base_entry[9] += entry[9]
        # pkt
        base_entry[10] += entry[10]

    @process_time_log
    def create_features(self, label):
        """Creates new features based on bytes, packtes and flow duration.

        When aggregation is done first, the flows are aggregated to later
        compute the new features.

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
    """Extracts features to be used by the machine learning algorithms.

    Attributes
    ----------
    self.selected_features: list
        Chosen features to be used by the machine learning algorithms."""

    def __init__(self, selected_features):
        self.selected_features = selected_features

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
                tmp.append(entry[idx])
            features.append(tmp)
            labels.append(entry[-1])

        return features, labels


# preprocessing methods to be used by detection instance.
preprocessing_obj = {
    'normal': None,
    'max_absolute_scaler': MaxAbsScaler(),
    'min_max_scaler': MinMaxScaler(),
    'robust_scaler': RobustScaler(),
    'standard_scaler': StandardScaler(),
    'normalizer': Normalizer(),
    'quantile_transformer': QuantileTransformer(output_distribution='normal')
}
