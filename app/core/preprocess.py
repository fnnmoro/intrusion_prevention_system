import ast
from datetime import datetime

from sklearn.preprocessing import (StandardScaler, MinMaxScaler,
                                   MaxAbsScaler, RobustScaler,
                                   QuantileTransformer, Normalizer)

from app.core.tools import process_time_log


class Formatter:
    """Formats the IP flows to be used by machine learning algorithms.

    The formatted IP flows can be used in the Modifier class.

    Attributes
    ----------
    self.header: list of list
        Features description.
    self.flows: list of list
        IP flows.
    self.gather: bool
        Signals the gathering process.
    self.train: bool
        Signals the training process."""

    def __init__(self, header, flows, gather=True, train=False):
        self.header = header
        self.flows = flows
        self.gather = gather
        self.train = train

    @process_time_log
    def format_header(self):
        """Format the header.

        Returns
        -------
        list of list
            Formatted header."""

        self.delete_features(self.header)
        self.sort_features(self.header)

        return self.header

    @process_time_log
    def format_flows(self):
        """Formats the flows to be used by the machine learning algorithms.

        Returns
        -------
        list of list
            Formatted IP flows."""

        if self.gather:
            # deletes the summary lines
            del self.flows[-3:]

        for flow in self.flows:
            if not self.train:
                self.delete_features(flow)
                self.sort_features(flow)
                self.replace_features(flow)
                self.count_flags(flow)
            self.convert_features(flow)

        return self.flows

    def delete_features(self, flow):
        """Deletes non-discriminative features.

        Parameters
        ----------
        flow: list
            IP flow."""

        # fwd and stos
        del flow[9:11]
        # from opkt to the end
        del flow[11:]

    def sort_features(self, flow):
        """Sorts the features in a specific order.

        Parameters
        ----------
        flow: list
            IP flow."""

        # updates existing flow with the new order
        flow[:] = [flow[idx] for idx in [0, 1, 3, 4, 7, 8, 5, 6, 2, 9, 10]]

    def replace_features(self, flow):
        """Replaces the missing features.

        Parameters
        ----------
        flow: list
            IP flow."""

        default_values = {0: '0001-01-01 01:01:01', 1: '0001-01-01 01:01:01',
                          2: '000.000.000.000', 3: '000.000.000.000',
                          4: 'NONE', 5: '......', 6: '0', 7: '0',
                          8: '0', 9: '0', 10: '0'}

        for idx, feature in enumerate(flow):
            # checks missing features
            if not feature:
                flow[idx] = default_values[idx]

    def convert_features(self, flow):
        """Converts the features to specific data types.

        Parameters
        ----------
        flow: list
            IP flow."""

        flow[0:2] = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
                      for i in flow[0:2]]
        flow[8] = round(float(flow[8]))
        flow[9:] = [int(i) for i in flow[9:]]

        # checks if is in the train mode to convert properly
        if self.train:
            flow[5:8] = [ast.literal_eval(feat) for feat in flow[5:8]]

    def count_flags(self, flow):
        """Counts TCP flags.

        Parameters
        ----------
        flow: list
            IP flow."""

        # checks if is the tcp protocol
        if flow[4] == 'TCP':
            # flags order
            flags = ['U', 'A', 'S', 'F', 'R', 'P']
            # filters only the flags
            flow[5] = [flag for flag in flow[5] if flag != '.']
            # creates a new list with the flags order and the count of them
            flow[5] = [flow[5].count(flag) for flag in flags]
        else:
            flow[5] = [0]


class Modifier:
    """Modifies the formatted IP flows to aggregate and create more
    discriminating features to be used by the machine learning algorithms.

    Attributes
    ----------
    self.header: list of list
        Formatted features description.
    self.flows: list of list
        Formatted IP flows.
    label: int
        Flow class.
    self.threshold: int
        Aggregation threshold to prevent that mulitple flows become just
        one."""

    def __init__(self, header, flows, label, threshold):
        self.header = header
        self.flows = flows
        self.label = label
        self.threshold = threshold

    def extend_header(self):
        """Extendes header according to new aggregations features.

        Returns
        -------
        self.header: list of list
            Extended features description."""

        self.header.extend(['bps', 'bpp', 'pps', 'nsp', 'ndp', 'flw', 'lbl'])

        return self.header

    @process_time_log
    def aggregate_flow(self):
        """Aggregates a formatted IP flow according to a established threshold.

        The flow are aggregated considering the same start hour and minute,
        source address, destination address and protocol.

        The threshold is useful when the flow to be aggregate are anomalous,
        like a DoS attack.

        Returns
        -------
        self.flow: list
            Modified IP flow."""

        # separates the first flow that will be matched against the others
        # use only the right features when intrusions flow
        base = self.flows.pop(0)[:11]

        # keeps only the unique ports
        sp = {base[6]}
        dp = {base[7]}

        # compares the value with the established threshold
        # 1 is used instead of 0 because a flow is separated first
        count = 1
        # compares the base flow with the rest of the flows
        for idx, flow in enumerate(self.flows):
            # checks if the threshold was reached
            if count != self.threshold:
                # default rules for aggregation
                rules = [base[0].hour == flow[0].hour,
                         base[0].minute == flow[0].minute,
                         base[2:5] == flow[2:5]]

                if all(rules):
                    # avoiding entries out of order
                    if base[1] < flow[1]:
                        base[1] = flow[1]
                    base[5] = [x+y for x, y in zip(base[5], flow[5])]
                    base[8] = base[1] - base[0]
                    base[9] += flow[9]
                    base[10] += flow[10]
                    sp.add(flow[6])
                    dp.add(flow[7])
                    # marks the flow that was aggregated
                    self.flows[idx] = [None]
                    count += 1
            else:
                break
        base[6] = sp
        base[7] = dp
        # counts the quantity of unique ports
        base.append(len(sp))
        base.append(len(dp))
        # time duration recalculed
        base[8] = (base[1] - base[0]).seconds
        # number of aggregated flows
        base.append(count)

        self.create_features(base)

        # checks if aggregation happened
        if count > 1:
            # filters only the not aggregated flows
            self.flows = [flow for flow in self.flows if flow != [None]]

        return base

    @process_time_log
    def create_features(self, base):
        """Creates new features based on bytes, packtes and flow duration.

        Parameters
        ----------
        base: list
            IP flow base."""

        # default value
        bps, bpp, pps = [0, 0, 0]

        # checks if the time duration isn't zero
        if base[8]:
            # bytes per second
            bps = int(round(base[10] / base[8]))
            # packet per second
            pps = int(round(base[9] / base[8]))

        # checks if the packet value isn't zero
        if base[9]:
            # bytes per packet
            bpp = int(round(base[10] / base[9]))

        base[11:11] = [bps, bpp, pps]
        base.append(self.label)


class Extractor:
    """Extracts features to be used by the machine learning algorithms.

    Attributes
    ----------
    self.selected_features: list
        Chosen features to be used by the machine learning algorithms."""

    def __init__(self, selected_features):
        self.selected_features = selected_features

    @process_time_log
    def extract_features(self, flow):
        """Extracts features and label from flow.

        Parameters
        ----------
        flow: list
            Formatted and modified flow.

        Returns
        -------
        list
            Features and label to be split into appropriate sets."""

        features, label = list(), list()

        for idx in self.selected_features:
            features.append(flow[idx])
        label.append(flow[-1])

        return features, label


# preprocessing methods to be used by detection instance.
preprocessing_obj = {
    'none': None,
    'max_absolute_scaler': MaxAbsScaler(),
    'min_max_scaler': MinMaxScaler(),
    'robust_scaler': RobustScaler(),
    'standard_scaler': StandardScaler(),
    'normalizer': Normalizer(),
    'quantile_transformer': QuantileTransformer(output_distribution='normal')
}
