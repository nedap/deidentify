import csv
import itertools
from collections import defaultdict
from typing import List


class Metric:
    """
    Compute evaluation metrics.

    Source:
    https://github.com/zalandoresearch/flair/blob/master/flair/training_utils.py
    """

    def __init__(self, name):
        self.name = name

        self._tps = defaultdict(int)
        self._fps = defaultdict(int)
        self._tns = defaultdict(int)
        self._fns = defaultdict(int)

    def add_tp(self, class_name, N=1):
        self._tps[class_name] += N

    def add_tn(self, class_name, N=1):
        self._tns[class_name] += N

    def add_fp(self, class_name, N=1):
        self._fps[class_name] += N

    def add_fn(self, class_name, N=1):
        self._fns[class_name] += N

    def get_tp(self, class_name=None):
        if class_name is None:
            return sum([self._tps[class_name] for class_name in self.get_classes()])
        return self._tps[class_name]

    def get_tn(self, class_name=None):
        if class_name is None:
            return sum([self._tns[class_name] for class_name in self.get_classes()])
        return self._tns[class_name]

    def get_fp(self, class_name=None):
        if class_name is None:
            return sum([self._fps[class_name] for class_name in self.get_classes()])
        return self._fps[class_name]

    def get_fn(self, class_name=None):
        if class_name is None:
            return sum([self._fns[class_name] for class_name in self.get_classes()])
        return self._fns[class_name]

    def precision(self, class_name=None):
        if self.get_tp(class_name) + self.get_fp(class_name) > 0:
            return round(self.get_tp(class_name) / (self.get_tp(class_name) + self.get_fp(class_name)), 4)
        return 0.0

    def recall(self, class_name=None):
        if self.get_tp(class_name) + self.get_fn(class_name) > 0:
            return round(self.get_tp(class_name) / (self.get_tp(class_name) + self.get_fn(class_name)), 4)
        return 0.0

    def f_score(self, class_name=None):
        if self.precision(class_name) + self.recall(class_name) > 0:
            return round(2 * (self.precision(class_name) * self.recall(class_name)) /
                         (self.precision(class_name) + self.recall(class_name)), 4)
        return 0.0

    def accuracy(self, class_name=None):
        if self.get_tp(class_name) + self.get_fp(class_name) + self.get_fn(class_name) > 0:
            return round(
                (self.get_tp(class_name)) /
                (self.get_tp(class_name) + self.get_fp(class_name) + self.get_fn(class_name)),
                4)
        return 0.0

    def micro_avg_f_score(self):
        return self.f_score(None)

    def macro_avg_f_score(self):
        class_f_scores = [self.f_score(class_name) for class_name in self.get_classes()]

        if class_f_scores:
            return sum(class_f_scores) / len(class_f_scores)

        return 0.0

    def micro_avg_accuracy(self):
        return self.accuracy(None)

    def macro_avg_accuracy(self):
        class_accuracy = [self.accuracy(class_name) for class_name in self.get_classes()]

        if class_accuracy:
            return round(sum(class_accuracy) / len(class_accuracy), 4)

        return 0.0

    def get_classes(self) -> List:
        all_classes = set(itertools.chain(*[list(keys) for keys
                                            in [self._tps.keys(), self._fps.keys(), self._tns.keys(),
                                                self._fns.keys()]]))
        all_classes = [class_name for class_name in all_classes if class_name is not None]
        all_classes.sort()
        return all_classes

    def to_csv(self, out_path):
        with open(out_path, mode='w') as out_file:
            metric_writer = csv.writer(out_file, delimiter=',', quotechar='"',
                                       quoting=csv.QUOTE_MINIMAL)
            metric_writer.writerow(['class_name', 'tp', 'fp', 'fn', 'tn', 'precision', 'recall',
                                    'accuracy', 'f1_score'])
            all_classes = self.get_classes()
            all_classes = [None] + all_classes
            for class_name in all_classes:
                metric_writer.writerow([
                    self.name if class_name is None else class_name,
                    self.get_tp(class_name),
                    self.get_fp(class_name),
                    self.get_fn(class_name),
                    self.get_tn(class_name),
                    self.precision(class_name),
                    self.recall(class_name),
                    self.accuracy(class_name),
                    self.f_score(class_name)
                ])

    def __str__(self):
        all_classes = self.get_classes()
        all_classes = [None] + all_classes
        all_lines = [
            '{0:<20}\ttp: {1:<5} - fp: {2:<5} - fn: {3:<5} - tn: {4:<5} - precision: {5:.4f} - recall: {6:.4f} - accuracy: {7:.4f} - f1-score: {8:.4f}'.format(
                self.name if class_name is None else class_name,
                self.get_tp(class_name), self.get_fp(class_name), self.get_fn(
                    class_name), self.get_tn(class_name),
                self.precision(class_name), self.recall(class_name), self.accuracy(class_name),
                self.f_score(class_name))
            for class_name in all_classes]
        return '\n'.join(all_lines)
