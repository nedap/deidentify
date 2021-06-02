import argparse
import os
from os.path import join

from flair.trainers import ModelTrainer
from loguru import logger
from numpy.random import RandomState

from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.evaluation.evaluator import Evaluator
from deidentify.methods import train_utils
from deidentify.methods.bilstmcrf import flair_utils, run_bilstmcrf
from deidentify.tokenizer import TokenizerFactory


def _ignore_sentence(sent):
    return sent[0].text.startswith('===')


def main(args, model_dir):
    logger.info('Args = {}'.format(args))
    corpus = CorpusLoader().load_corpus(CORPUS_PATH[args.corpus])
    tokenizer = TokenizerFactory().tokenizer(args.corpus)
    logger.info('Loaded corpus: {}'.format(corpus))

    logger.info('Get sentences...')
    train_sents, _ = flair_utils.standoff_to_flair_sents(
        corpus.train, tokenizer, verbose=True)
    dev_sents, _ = flair_utils.standoff_to_flair_sents(
        corpus.dev, tokenizer, verbose=True)
    test_sents, test_docs = flair_utils.standoff_to_flair_sents(corpus.test,
                                                                tokenizer, verbose=True)

    train_sents = train_sents + dev_sents
    train_sents_filtered = list(
        filter(lambda sent: not _ignore_sentence(sent), train_sents))

    sample_size = int(len(train_sents_filtered) * args.train_sample_frac)
    rs = RandomState(seed=args.random_seed)
    train_sents_sample = rs.choice(
        train_sents_filtered, replace=False, size=sample_size).tolist()
    logger.info('Train with fraction of training data: {} sents out of {} sentences ({}%)',
                sample_size, len(train_sents_filtered), args.train_sample_frac)

    # We need to pass some dev data, otherwise flair raises a ZeroDivisionError
    # See: https://github.com/zalandoresearch/flair/issues/1139
    # We just split the training sample into half and instruct Flair to train_with_dev (see below).
    half = len(train_sents_sample) // 2
    flair_corpus = flair_utils.FilteredCorpus(train=train_sents_sample[:half],
                                              dev=train_sents_sample[half:],
                                              test=test_sents,
                                              ignore_sentence=_ignore_sentence)
    logger.info(flair_corpus)

    logger.info('Train model...')
    tagger = run_bilstmcrf.get_model(flair_corpus,
                                     corpus_name=args.corpus,
                                     embedding_lang=args.embedding_lang,
                                     pooled_contextual_embeddings=True)

    trainer = ModelTrainer(tagger, flair_corpus)
    trainer.train(join(model_dir, 'flair'),
                  max_epochs=150,
                  monitor_train=False,
                  train_with_dev=True,
                  save_final_model=args.save_final_model)

    logger.info('Make predictions...')
    run_bilstmcrf.make_predictions(tagger, flair_corpus)

    logger.info('Start evaluation...')
    evaluator = Evaluator(gold=corpus.test,
                          predicted=flair_utils.flair_sents_to_standoff(test_sents, test_docs))

    entity_level_metric = evaluator.entity_level()
    logger.info('\n{}', entity_level_metric)
    entity_level_metric.to_csv(join(model_dir, 'scores_entity.csv'))
    evaluator.token_level().to_csv(join(model_dir, 'scores_token.csv'))
    evaluator.token_level_blind().to_csv(join(model_dir, 'scores_token_blind.csv'))
    logger.info('Done.')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", choices=CORPUS_PATH.keys(),
                        help="Corpus identifier.")
    parser.add_argument("run_id", help="Run identifier")
    parser.add_argument("--train_sample_frac",
                        help="Fraction of the training data to use.",
                        type=float,
                        default=0.1)
    parser.add_argument("--random_seed",
                        help="Seed for the training set sampler.",
                        type=int,
                        default=42)
    parser.add_argument("--save_final_model",
                        help="If passed, the final model is saved.",
                        action='store_true')
    parser.add_argument("--embedding_lang",
                        choices=['en', 'nl', 'fr'],
                        help="Specify language of embeddings.")
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    ARGS.run_id = 'bilstmcrf_{}_frac_{}_seed_{}'.format(ARGS.run_id,
                                                        ARGS.train_sample_frac,
                                                        ARGS.random_seed)
    MODEL_DIR = train_utils.model_dir(ARGS.corpus + '-subsets', ARGS.run_id)
    os.makedirs(MODEL_DIR, exist_ok=True)
    logger.add(join(MODEL_DIR, 'training.log'))
    main(ARGS, MODEL_DIR)
