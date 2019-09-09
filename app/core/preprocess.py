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

    def __init__(self, gather=True, train=False):
        self.gather = gather
        self.train = train

    def format_header(self, header):
        """Format the header.

        Returns
        -------
        list of list
            Formatted header."""

        self.delete_features(header)
        self.sort_features(header)

        return header

    @process_time_log
    def format_flows(self, flows):
        """Formats the flows to be used by the machine learning algorithms.

        Returns
        -------
        list of list
            Formatted IP flows."""

        if self.gather:
            # deleting summary lines.
            del flows[-3:]

        for flow in flows:
            if not self.train:
                self.delete_features(flow)
                self.sort_features(flow)
                self.replace_features(flow)
                self.count_flags(flow)
            self.convert_features(flow)

        return flows

    def delete_features(self, flow):
        """Deletes non-discriminative features.

        Parameters
        ----------
        flow: list
            IP flow."""

        # fwd and stos.
        del flow[9:11]
        # from opkt to the end.
        del flow[11:]

    def sort_features(self, flow):
        """Sorts the features in a specific order.

        Parameters
        ----------
        flow: list
            IP flow."""

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

        # evaluating an expression.
        if self.train:
            flow[5:8] = [ast.literal_eval(feat) for feat in flow[5:8]]

    def count_flags(self, flow):
        """Counts TCP flags.

        Parameters
        ----------
        flow: list
            IP flow."""

        if flow[4] == 'TCP':
            flags = ['U', 'A', 'S', 'F', 'R', 'P']
            # filtering only the flags.
            flow[5] = [flag for flag in flow[5] if flag != '.']
            # new list with flags order and count.
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

    def __init__(self, label, threshold):
        self.label = label
        self.threshold = threshold

    def extend_header(self, header):
        """Extendes header according to new aggregations features.

        Returns
        -------
        self.header: list of list
            Extended features description."""

        header.extend(['bps', 'bpp', 'pps', 'nsp', 'ndp', 'flw', 'lbl'])

        return header

    @process_time_log
    def aggregate_flows(self, flows):
        #self.flows = flows
        agg_flows = list()

        while flows:
            agg_flow, flows = self.aggregate(flows)
            agg_flows.append(agg_flow)

        return agg_flows

    def aggregate(self, flows):
        """Aggregates a formatted IP flow according to a established threshold.

        The flow are aggregated considering the same start hour and minute,
        source address, destination address and protocol.

        The threshold is useful when the flow to be aggregate are anomalous,
        like a DoS attack.

        Returns
        -------
        self.flow: list
            Modified IP flow."""

        # separating the flow that will be matched against the others.
        base = flows.pop(0)

        # keeps only the unique ports.
        sp = {base[6]}
        dp = {base[7]}
        # 1 is used instead of 0 because the base flow.
        agg = 1

        # comparing the base flow with the rest of the flows.
        for idx, flow in enumerate(flows):
            # checking if threshold was reached.
            if agg != self.threshold:
                rules = [base[0].hour == flow[0].hour,
                         base[0].minute == flow[0].minute,
                         base[2:5] == flow[2:5]]

                if all(rules):
                    # avoiding flows out of order.
                    if base[1] < flow[1]:
                        base[1] = flow[1]
                    base[5] = [x+y for x, y in zip(base[5], flow[5])]
                    base[8] = base[1] - base[0]
                    base[9] += flow[9]
                    base[10] += flow[10]
                    sp.add(flow[6])
                    dp.add(flow[7])
                    # marking aggregated flows.
                    flows[idx] = [None]
                    agg += 1
            else:
                break

        base[6] = sp
        base[7] = dp
        # counting unique ports.
        base.append(len(sp))
        base.append(len(dp))
        # recalculating time duration.
        base[8] = (base[1] - base[0]).seconds
        # number of aggregated flows.
        base.append(agg)
        self.create_features(base)

        if agg > 1:
            # filtering only the remaining flows.
            flows = [flow for flow in flows if flow[0]]

        return base, flows

    def create_features(self, base):
        """Creates new features based on bytes, packtes and flow duration.

        Parameters
        ----------
        base: list
            IP flow base."""

        bps, pps = 0, 0

        # checking if the time duration isn't zero
        if base[8]:
            # bytes per second
            bps = int(round(base[10] / base[8]))
            # packet per second
            pps = int(round(base[9] / base[8]))

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
    def extract_features_labels(self, flows):
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
        for flow in flows:
            feat, lbl = self.extract(flow)
            features.append(feat)
            labels.append(lbl)

        return features, labels

    def extract(self, flow):
        """Extracts features and label from a unique flow.

        Parameters
        ----------
        flow: list
            Formatted and modified flow.

        Returns
        -------
        list
            Features and label."""

        features = list()
        label = -1

        for idx in self.selected_features:
            features.append(flow[idx])
        label = flow[-1]

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
