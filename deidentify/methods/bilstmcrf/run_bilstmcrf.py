import argparse
import os
from functools import partial
from os.path import join
from typing import List

import flair.data
from flair.embeddings import (FlairEmbeddings, PooledFlairEmbeddings, StackedEmbeddings,
                              TokenEmbeddings, WordEmbeddings)
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from loguru import logger

from deidentify.methods import train_utils
from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.methods.bilstmcrf import flair_utils
from deidentify.tokenizer import TokenizerFactory


def _ignore_sentence(sent):
    return sent[0].text.startswith('===')


def _predict_ignored(sents):
    for sent in sents:
        for token in sent:
            token.add_tag('ner', 'O')


def make_predictions(tagger, filtered_corpus: flair_utils.FilteredCorpus):
    tagger.predict(filtered_corpus.train)
    tagger.predict(filtered_corpus.dev)
    tagger.predict(filtered_corpus.test)

    _predict_ignored(filtered_corpus.train_ignored)
    _predict_ignored(filtered_corpus.dev_ignored)
    _predict_ignored(filtered_corpus.test_ignored)


def get_embeddings(corpus_name: str, pooled: bool,
                   contextual_forward_path: str = None,
                   contextual_backward_path: str = None) -> List[TokenEmbeddings]:
    if corpus_name.startswith('ons'):
        logger.info('Use Dutch embeddings')
        word_embeddings = 'nl'
        contextual_forward = 'nl-forward'
        contextual_backward = 'nl-backward'
    else:
        logger.info('Use English embeddings')
        word_embeddings = 'glove'
        contextual_forward = 'news-forward'
        contextual_backward = 'news-backward'

    if contextual_forward_path:
        contextual_forward = contextual_forward_path
    if contextual_backward_path:
        contextual_backward = contextual_backward_path

    if pooled:
        logger.info('Use PooledFlairEmbeddings with mean pooling')
        ContextualEmbeddings = partial(PooledFlairEmbeddings, pooling='mean')
    else:
        logger.info('Use FlairEmbeddings')
        ContextualEmbeddings = FlairEmbeddings

    embedding_types: List[TokenEmbeddings] = [
        WordEmbeddings(word_embeddings),
        ContextualEmbeddings(contextual_forward),
        ContextualEmbeddings(contextual_backward),
    ]

    return embedding_types


def get_model(corpus: flair.data.Corpus,
              corpus_name: str,
              pooled_contextual_embeddings: bool,
              contextual_forward_path: str = None,
              contextual_backward_path: str = None):
    tag_type = 'ner'
    tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)

    embedding_types: List[TokenEmbeddings] = get_embeddings(
        corpus_name=corpus_name,
        pooled=pooled_contextual_embeddings,
        contextual_forward_path=contextual_forward_path,
        contextual_backward_path=contextual_backward_path
    )

    embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)
    tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                            embeddings=embeddings,
                                            tag_dictionary=tag_dictionary,
                                            tag_type=tag_type)
    return tagger


def main(args):
    logger.info('Args = {}'.format(args))
    corpus = CorpusLoader().load_corpus(CORPUS_PATH[args.corpus])
    tokenizer = TokenizerFactory().tokenizer(args.corpus)

    logger.info('Loaded corpus: {}'.format(corpus))
    model_dir = train_utils.model_dir(corpus.name, args.run_id)
    os.makedirs(model_dir, exist_ok=True)

    logger.info('Get sentences...')
    train_sents, train_docs = flair_utils.standoff_to_flair_sents(corpus.train, tokenizer,
                                                                  verbose=True)
    dev_sents, dev_docs = flair_utils.standoff_to_flair_sents(corpus.dev, tokenizer, verbose=True)
    test_sents, test_docs = flair_utils.standoff_to_flair_sents(corpus.test, tokenizer,
                                                                verbose=True)

    flair_corpus = flair_utils.FilteredCorpus(train=train_sents,
                                              dev=dev_sents,
                                              test=test_sents,
                                              ignore_sentence=_ignore_sentence)
    logger.info(flair_corpus)

    if not args.model_file:
        logger.info('Train model...')
        tagger = get_model(flair_corpus,
                           corpus_name=args.corpus,
                           pooled_contextual_embeddings=args.pooled_contextual_embeddings,
                           contextual_forward_path=args.contextual_forward_path,
                           contextual_backward_path=args.contextual_backward_path)

        trainer = ModelTrainer(tagger, flair_corpus)
        trainer.train(join(model_dir, 'flair'),
                      max_epochs=150,
                      monitor_train=False,
                      train_with_dev=args.train_with_dev)

        if not args.train_with_dev:
            # Model performance is judged by dev data, so we also pick the best performing model
            # according to the dev score to make our final predictions.
            tagger = SequenceTagger.load(join(model_dir, 'flair', 'best-model.pt'))
        else:
            # Training is stopped if train loss converges - here, we do not have a "best model" and
            # use the final model to make predictions.
            pass
    else:
        logger.info('Load existing model from {}'.format(args.model_file))
        tagger = SequenceTagger.load(args.model_file)

    logger.info('Make predictions...')
    make_predictions(tagger, flair_corpus)

    train_utils.save_predictions(corpus_name=corpus.name, run_id=args.run_id,
                                train=flair_utils.flair_sents_to_standoff(train_sents, train_docs),
                                dev=flair_utils.flair_sents_to_standoff(dev_sents, dev_docs),
                                test=flair_utils.flair_sents_to_standoff(test_sents, test_docs))


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", choices=CORPUS_PATH.keys(), help="Corpus identifier.")
    parser.add_argument("run_id", help="Run identifier")
    parser.add_argument("--train_with_dev", help="Use dev set during training",
                        action='store_true')
    parser.add_argument("--model_file", help="Load existing model instead of training new.")
    parser.add_argument("--pooled_contextual_embeddings",
                        help="Boolean flag whether to use pooled variant of FlairEmbeddings.",
                        action='store_true')
    parser.add_argument("--contextual_forward_path",
                        help="Path to contextual string embeddings (forward)")
    parser.add_argument("--contextual_backward_path",
                        help="Path to contextual string embeddings (backward)")
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    ARGS.run_id = 'bilstmcrf_' + ARGS.run_id
    logger.add(join(train_utils.model_dir(ARGS.corpus, ARGS.run_id), 'training.log'))
    main(ARGS)
