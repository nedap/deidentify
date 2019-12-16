import argparse
import os
import pickle
from os.path import join

from loguru import logger

from deidentify.methods import train_utils
from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.methods import tagging_utils
from deidentify.methods.crf import crf_labeler, crf_util
from deidentify.tokenizer import TokenizerFactory


def main(args):
    logger.info('Args = {}'.format(args))
    corpus = CorpusLoader().load_corpus(CORPUS_PATH[args.corpus])
    tokenizer = TokenizerFactory().tokenizer(args.corpus)
    logger.info('Loaded corpus: {}'.format(corpus))

    model_dir = train_utils.model_dir(corpus.name, args.run_id)
    os.makedirs(model_dir, exist_ok=True)

    logger.info('Get sentences...')
    train_sents, train_docs = tagging_utils.standoff_to_sents(corpus.train, tokenizer, verbose=True)
    dev_sents, dev_docs = tagging_utils.standoff_to_sents(corpus.dev, tokenizer, verbose=True)
    test_sents, test_docs = tagging_utils.standoff_to_sents(corpus.test, tokenizer, verbose=True)

    logger.info('Compute features...')
    feature_extractor, meta_sentence_filter = crf_util.FEATURE_EXTRACTOR[args.feature_extractor]
    X_train, y_train = crf_labeler.sents_to_features_and_labels(train_sents, feature_extractor)
    X_dev, y_dev = crf_labeler.sents_to_features_and_labels(dev_sents, feature_extractor)
    X_test, _ = crf_labeler.sents_to_features_and_labels(test_sents, feature_extractor)

    logger.info('len(X_train) = {}'.format(len(X_train)))
    logger.info('len(y_train) = {}'.format(len(y_train)))
    logger.info('len(X_dev) = {}'.format(len(X_dev)))
    logger.info('len(X_test) = {}'.format(len(X_test)))

    if not args.model_file:
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
    else:
        with open(args.model_file, 'rb') as clf_file:
            crf = pickle.load(clf_file)
        logger.info('Loaded existing CRF: {}'.format(crf))

    logger.info('CRF classes: {}'.format(crf.classes_))

    logger.info('Make predictions...')
    y_pred_train = crf.predict(X_train)
    y_pred_dev = crf.predict(X_dev)
    y_pred_test = crf.predict(X_test)

    train_utils.save_predictions(corpus_name=corpus.name, run_id=args.run_id,
                                train=tagging_utils.sents_to_standoff(y_pred_train, train_docs),
                                dev=tagging_utils.sents_to_standoff(y_pred_dev, dev_docs),
                                test=tagging_utils.sents_to_standoff(y_pred_test, test_docs))

    logger.info('Save model artifacts...')
    labels = list(crf.classes_)
    labels.remove('O')
    crf_util.save_bio_report(y_true=y_dev, y_pred=y_pred_dev, labels=labels, out_dir=model_dir)
    crf_util.save_transition_features(crf, model_dir)
    crf_util.save_state_features(crf, model_dir)
    crf_util.persist_model(crf, model_dir)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", choices=CORPUS_PATH.keys(), help="Corpus identifier.")
    parser.add_argument("run_id", help="Run identifier")
    parser.add_argument("feature_extractor", choices=crf_util.FEATURE_EXTRACTOR.keys(),
                        help="Feature extractor.")
    parser.add_argument("--model_file", help="Trained CRF model file (i.e., full path to .pickle)")
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    ARGS.run_id = 'crf_' + ARGS.run_id
    logger.add(join(train_utils.model_dir(ARGS.corpus, ARGS.run_id), 'training.log'))
    main(ARGS)
