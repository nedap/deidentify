import argparse
import os
from os.path import join

from loguru import logger
from numpy.random import RandomState

from deidentify.methods import train_utils
from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.evaluation.evaluator import Evaluator
from deidentify.methods import tagging_utils
from deidentify.methods.crf import crf_labeler, crf_util
from deidentify.tokenizer import TokenizerFactory


def _is_not_meta_sentence(sent):
    return not sent[0].text.startswith('===')


def main(args, model_dir):
    logger.info('Args = {}'.format(args))
    corpus = CorpusLoader().load_corpus(CORPUS_PATH[args.corpus])
    tokenizer = TokenizerFactory().tokenizer(args.corpus)
    logger.info('Loaded corpus: {}'.format(corpus))

    logger.info('Get sentences...')
    train_sents, _ = tagging_utils.standoff_to_sents(corpus.train, tokenizer, verbose=True)
    dev_sents, _ = tagging_utils.standoff_to_sents(corpus.dev, tokenizer, verbose=True)
    test_sents, test_docs = tagging_utils.standoff_to_sents(corpus.test, tokenizer, verbose=True)

    train_sents = train_sents + dev_sents
    train_sents_filtered = list(filter(_is_not_meta_sentence, train_sents))

    sample_size = int(len(train_sents_filtered) * args.train_sample_frac)
    rs = RandomState(seed=args.random_seed)
    train_sents_sample = rs.choice(train_sents_filtered, replace=False, size=sample_size).tolist()
    logger.info('Train with fraction of training data: {} sents out of {} sentences ({}%)',
                sample_size, len(train_sents_filtered), args.train_sample_frac)

    logger.info('Compute features...')
    feature_extractor, meta_sentence_filter = crf_util.FEATURE_EXTRACTOR[args.feature_extractor]
    X_train, y_train = crf_labeler.sents_to_features_and_labels(train_sents_sample,
                                                                feature_extractor)
    X_test, _ = crf_labeler.sents_to_features_and_labels(test_sents, feature_extractor)

    logger.info('len(X_train) = {}'.format(len(X_train)))
    logger.info('len(y_train) = {}'.format(len(y_train)))
    logger.info('len(X_test) = {}'.format(len(X_test)))

    crf = crf_labeler.SentenceFilterCRF(
        ignore_sentence=meta_sentence_filter,
        ignored_label='O',
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )
    logger.info('Start training... {}'.format(crf))
    crf.fit(X_train, y_train)

    logger.info('CRF classes: {}'.format(crf.classes_))

    logger.info('Make predictions...')
    y_pred_test = crf.predict(X_test)

    logger.info('Start evaluation...')
    evaluator = Evaluator(gold=corpus.test,
                          predicted=tagging_utils.sents_to_standoff(y_pred_test, test_docs))

    entity_level_metric = evaluator.entity_level()
    logger.info('\n{}', entity_level_metric)
    entity_level_metric.to_csv(join(model_dir, 'scores_entity.csv'))
    evaluator.token_level().to_csv(join(model_dir, 'scores_token.csv'))
    evaluator.token_level_blind().to_csv(join(model_dir, 'scores_token_blind.csv'))
    logger.info('Done.')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", choices=CORPUS_PATH.keys(), help="Corpus identifier.")
    parser.add_argument("run_id", help="Run identifier")
    parser.add_argument("feature_extractor", choices=crf_util.FEATURE_EXTRACTOR.keys(),
                        help="Feature extractor.")
    parser.add_argument("--train_sample_frac",
                        help="Fraction of the training data to use.",
                        type=float,
                        default=0.1)
    parser.add_argument("--random_seed",
                        help="Seed for the training set sampler.",
                        type=int,
                        default=42)
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    ARGS.run_id = 'crf_{}_frac_{}_seed_{}'.format(ARGS.run_id,
                                                  ARGS.train_sample_frac,
                                                  ARGS.random_seed)
    MODEL_DIR = train_utils.model_dir(ARGS.corpus + '-subsets', ARGS.run_id)
    os.makedirs(MODEL_DIR, exist_ok=True)
    logger.add(join(MODEL_DIR, 'training.log'))
    main(ARGS, MODEL_DIR)
