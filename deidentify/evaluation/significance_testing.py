import argparse
import csv
import os
from os.path import dirname, join
from typing import List

import yaml
from loguru import logger

from deidentify.base import Document
from deidentify.evaluation import evaluate_run, evaluator
from deidentify.evaluation.art import ApproximateRandomizationTest


def _load_yaml(yaml_file):
    with open(yaml_file, 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def noop():
    return None


def micro_f1(gold: List[Document], predicted: List[Document]):
    return evaluator.Evaluator(gold, predicted, tokenizer=noop).entity_level().f_score()


def micro_precision(gold: List[Document], predicted: List[Document]):
    return evaluator.Evaluator(gold, predicted, tokenizer=noop).entity_level().precision()


def micro_recall(gold: List[Document], predicted: List[Document]):
    return evaluator.Evaluator(gold, predicted, tokenizer=noop).entity_level().recall()


class SignificanceReport:

    def __init__(self, title, corpus, part, runs, metrics, trials=10000):
        self.title = title
        self.corpus = corpus
        self.part = part
        self.runs = runs
        self.trials = trials
        self.metrics = metrics
        out_dir = join(dirname(__file__), '../../output/evaluation', corpus)
        self.out_file = join(out_dir, 'significance.csv')
        os.makedirs(out_dir, exist_ok=True)

    def _corpus_path(self):
        return join(dirname(__file__), '../../data/corpus', self.corpus, self.part)

    def _predictions_path(self, run_id):
        return join(dirname(__file__), '../../output/predictions', self.corpus, run_id, self.part)

    def art_test(self, gold, run_a, run_b, metric):
        art = ApproximateRandomizationTest(gold, run_a, run_b, metric,
                                           trials=self.trials)
        return art.run()

    def make_report(self):
        logger.info('Generate significance report {}'.format(self.title))
        logger.info('Corpus = "{}" part = "{}"'.format(self.corpus, self.part))

        docs_path = self._corpus_path()
        gold_documents = evaluate_run.get_documents(docs_path=docs_path, anns_path=docs_path)

        with open(self.out_file, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['run_a', 'run_b', 'metric', 'p_value'])

            for pair in self.runs:
                pred_docs_run_a = evaluate_run.get_documents(
                    docs_path=docs_path, anns_path=self._predictions_path(pair['run_a']))
                pred_docs_run_b = evaluate_run.get_documents(
                    docs_path=docs_path, anns_path=self._predictions_path(pair['run_b']))

                for metric in self.metrics:
                    p_value = self.art_test(gold_documents, pred_docs_run_a, pred_docs_run_b,
                                            metric)
                    writer.writerow([pair['run_a'], pair['run_b'], metric.__name__, p_value])
                    logger.info('{} - {} - {}'.format(pair, metric.__name__, p_value))


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Significance test config file (.yaml)")
    parser.add_argument("--trials", help="Run identifier", default=10000, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    c = _load_yaml(ARGS.config_file)

    report = SignificanceReport(
        title=c['name'],
        corpus=c['corpus'],
        part=c['part'],
        runs=c['run_ids'],
        metrics=[
            micro_f1,
            micro_precision,
            micro_recall
        ],
        trials=ARGS.trials
    )

    report.make_report()
