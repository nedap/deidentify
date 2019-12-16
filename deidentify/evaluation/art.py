import math

import numpy as np
from joblib import Parallel, delayed

from tqdm import tqdm


class ApproximateRandomizationTest(object):
    """A paired two-sided approximate randomization test.
    This class allows performing a paired two-sided approximate randomization
    test to assess the statistical significance of the difference in
    performance between two systems which are run and measured on the same
    corpus.
    Adjusted original version (https://github.com/smartschat/art) to support paralellism.
    Attributes:
        system1_scores: A Scores object, which represents the scores of the
                        first system under consideration.
        system2_scores: A Scores object, which represents the scores of the
                        second system under consideration.
        aggregator: An aggregator function, which aggregates all scores for
                        individual documents to obtain a score for the whole
                        corpus.
        trials: The number of iterations during the test.
    """

    def __init__(self,
                 ground_truth,
                 system1_scores,
                 system2_scores,
                 metric,
                 trials=10000,
                 n_jobs=1):
        """Inits a paired two-sided approximate randomization test.
        Args:
            system1_scores: A Scores object, which represents the scores of the
                            first system under consideration.
            system2_scores: A Scores object, which represents the scores of the
                            second system under consideration.
            aggregator: An aggregator function, which aggregates all scores for
                            individual documents to obtain a score for the
                            whole corpus.
            trials: The number of iterations during the test. Defaults to
                            10000.
        """
        self.ground_truth = ground_truth
        self.system1_scores = system1_scores
        self.system2_scores = system2_scores
        self.metric = metric
        self.trials = trials
        self.n_jobs = n_jobs

    def _trial(self, absolute_difference):
        pseudo_system1_scores = []
        pseudo_system2_scores = []

        for score1, score2, rand in zip(self.system1_scores,
                                        self.system2_scores,
                                        np.random.randint(2, size=len(self.system1_scores))):
            if rand == 0:
                pseudo_system1_scores.append(score1)
                pseudo_system2_scores.append(score2)
            else:
                pseudo_system1_scores.append(score2)
                pseudo_system2_scores.append(score1)

        pseudo_difference = math.fabs(
            self.metric(self.ground_truth, pseudo_system1_scores) -
            self.metric(self.ground_truth, pseudo_system2_scores))

        if pseudo_difference >= absolute_difference:
            return 1
        return 0

    def run(self):
        """Compute the statistical significance of a difference between
        the systems via a paired two-sided approximate randomization test.
        Returns:
            An approximation of the probability of observing corpus-wide
            differences in scores at least as extreme as observed here, when
            there is no difference between the systems.
        """

        absolute_difference = math.fabs(
            self.metric(self.ground_truth, self.system1_scores) -
            self.metric(self.ground_truth, self.system2_scores))

        if self.n_jobs == 1:
            trials = [self._trial(absolute_difference) for _ in tqdm(range(self.trials))]
        else:
            trials = Parallel(n_jobs=self.n_jobs)(
                delayed(self._trial)(absolute_difference) for _ in range(self.trials))
        shuffled_was_at_least_as_high = sum(trials)

        p_value = (shuffled_was_at_least_as_high + 1) / (self.trials + 1)
        return p_value
