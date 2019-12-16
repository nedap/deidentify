import os
from os.path import dirname, join
from typing import List

import numpy as np
import scipy.stats
from loguru import logger

from deidentify.base import Document
from deidentify.dataset import brat

PREDICTIONS_PATH = join(dirname(__file__), '../../output/predictions')


class LogUniform():

    def __init__(self, a=-1, b=0, base=10):
        self.loc = a
        self.scale = b - a
        self.base = base

    def rvs(self, size=None, random_state=None):
        uniform = scipy.stats.uniform(loc=self.loc, scale=self.scale)
        if not size:
            return np.power(self.base, uniform.rvs(random_state=random_state))

        return np.power(self.base, uniform.rvs(size=size, random_state=random_state))


def model_dir(corpus_name, run_id):
    return join(PREDICTIONS_PATH, corpus_name, run_id)


def _save_predictions(path, documents: List[Document]):
    os.makedirs(path, exist_ok=True)

    for doc in documents:
        brat.write_brat_annotations(doc.annotations, join(path, '{}.ann'.format(doc.name)))


def save_predictions(corpus_name, run_id,
                     train: List[Document] = None,
                     test: List[Document] = None,
                     dev: List[Document] = None):

    for part_name, part_docs in zip(['train', 'test', 'dev'], [train, test, dev]):
        if not part_docs:
            continue

        logger.info('Write {}.{}.{} predictions (N = {})'.format(corpus_name, run_id, part_name,
                                                                 len(part_docs)))
        base_path = model_dir(corpus_name, run_id)
        _save_predictions(join(base_path, part_name), part_docs)
