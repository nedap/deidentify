"""
Evaluate all runs for a specific corpus and save output to a CSV file.

Only aggregate metrics over all classes are computed and saved as a summary. For a detailed
evaluation of a single run, use `deidentify.evaluation.evaluate_run`.
"""
import argparse
import glob
import os
from os.path import basename, dirname, join

import pandas as pd
from loguru import logger

from deidentify.evaluation.evaluate_run import evaluate

PREDICTIONS_PATH = join(dirname(__file__), '../../output/predictions/')
OUTPUT_PATH = join(dirname(__file__), '../../output/evaluation')
CORPUS_PATH = join(dirname(__file__), '../../data/corpus/')


def _language_for_corpus(corpus: str):
    if corpus.startswith('ons'):
        return 'nl'

    return 'en'


def main(args):
    runs = glob.glob(join(PREDICTIONS_PATH, args.corpus, '*'))
    logger.info('Number of runs: {}'.format(len(runs)))
    logger.info('Runs: {}'.format([basename(r) for r in runs]))

    output_path = join(OUTPUT_PATH, args.corpus)
    os.makedirs(output_path, exist_ok=True)

    for part in ['train', 'dev', 'test']:
        corpus_path = join(CORPUS_PATH, args.corpus, part)

        part_summary = []

        for run in runs:
            run_name = basename(run)
            logger.info('Evaluate {}-{}'.format(part, run_name))

            evaluator = evaluate(documents_path=corpus_path,
                                 gold_path=corpus_path,
                                 pred_path=join(run, part),
                                 language=_language_for_corpus(args.corpus))

            entity = evaluator.entity_level()
            token = evaluator.token_level()
            token_blind = evaluator.token_level_blind()

            part_summary.append((
                run_name,
                entity.precision(),
                entity.recall(),
                entity.f_score(),

                token.precision(),
                token.recall(),
                token.f_score(),

                token_blind.precision(),
                token_blind.recall(),
                token_blind.f_score(),

                entity.macro_avg_f_score(),
                token.macro_avg_f_score(),
                token_blind.macro_avg_f_score(),
            ))

        df_part = pd.DataFrame(part_summary, columns=[
            'run_id',
            'entity_precision',
            'entity_recall',
            'entity_f1',

            'token_precision',
            'token_recall',
            'token_f1',

            'token_blind_precision',
            'token_blind_recall',
            'token_blind_f1',

            'entity_macro_f1',
            'token_macro_f1',
            'token_blind_macro_f1',
        ])
        df_part \
            .sort_values('run_id') \
            .to_csv(join(output_path, 'summary_{}.csv'.format(part)), index=False)

    logger.info('Done.')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", help="Name of corpus (e.g., 'dummy', 'ons')", type=str)
    return parser.parse_args()


if __name__ == '__main__':
    logger.disable("deidentify.evaluation.evaluator")
    main(arg_parser())
