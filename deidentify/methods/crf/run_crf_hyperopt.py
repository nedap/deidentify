import argparse
import os
from os.path import join

from loguru import logger
from sklearn.metrics import make_scorer
from sklearn.model_selection import PredefinedSplit, RandomizedSearchCV
from sklearn.utils import parallel_backend
from sklearn_crfsuite.metrics import flat_f1_score

from deidentify.methods import train_utils
from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.methods import tagging_utils
from deidentify.methods.crf import crf_labeler, crf_util
from deidentify.tokenizer import TokenizerFactory

PARAM_SPACE = {
    'c1': train_utils.LogUniform(-4, 1),
    'c2': train_utils.LogUniform(-4, 1),
}


def _save_model_aritfacts(random_search, model_dir, y_test, y_pred_test):
    logger.info('Save model artifacts...')
    crf = random_search.best_estimator_
    labels = list(crf.classes_)
    labels.remove('O')
    crf_util.save_bio_report(y_true=y_test, y_pred=y_pred_test, labels=labels, out_dir=model_dir)
    crf_util.save_transition_features(crf, model_dir)
    crf_util.save_state_features(crf, model_dir)
    crf_util.persist_model(crf, model_dir)
    crf_util.plot_random_search_parameter_pair(join(model_dir, 'rs_results.pdf'),
                                               random_search.cv_results_,
                                               param_x='c1',
                                               param_y='c2')
    crf_util.save_rs_results(random_search.cv_results_, model_dir)


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
    X_test, y_test = crf_labeler.sents_to_features_and_labels(test_sents, feature_extractor)

    logger.info('len(X_train) = {}'.format(len(X_train)))
    logger.info('len(y_train) = {}'.format(len(y_train)))
    logger.info('len(X_dev) = {}'.format(len(X_dev)))
    logger.info('len(X_test) = {}'.format(len(X_test)))

    X_train_combined = X_train + X_dev
    y_train_combined = y_train + y_dev

    train_indices = [-1] * len(X_train)
    dev_indices = [0] * len(X_dev)
    test_fold = train_indices + dev_indices

    labels = list(set(label for sent in y_train_combined for label in sent))
    labels.remove('O')
    logger.info('Labels: {}'.format(labels))
    f1_scorer = make_scorer(flat_f1_score, labels=labels, average='micro')

    crf = crf_labeler.SentenceFilterCRF(
        ignore_sentence=meta_sentence_filter,
        ignored_label='O',
        algorithm='lbfgs',
        max_iterations=100,
        all_possible_transitions=True
    )

    ps = PredefinedSplit(test_fold)
    rs = RandomizedSearchCV(crf, PARAM_SPACE,
                            cv=ps,
                            verbose=1,
                            n_jobs=args.n_jobs,
                            n_iter=args.n_iter,
                            scoring=f1_scorer,
                            return_train_score=True)

    logger.info('Start RandomizedSearchCV... {}'.format(crf))
    with parallel_backend('multiprocessing'):
        rs.fit(X_train_combined, y_train_combined)

    logger.info('best params: {}'.format(rs.best_params_))
    logger.info('best CV score: {}'.format(rs.best_score_))
    logger.info('model size: {:0.2f}M'.format(rs.best_estimator_.size_ / 1000000))

    logger.info('Make predictions...')
    crf = rs.best_estimator_
    y_pred_train = crf.predict(X_train)
    y_pred_dev = crf.predict(X_dev)
    y_pred_test = crf.predict(X_test)

    train_utils.save_predictions(corpus_name=corpus.name, run_id=args.run_id,
                                train=tagging_utils.sents_to_standoff(y_pred_train, train_docs),
                                dev=tagging_utils.sents_to_standoff(y_pred_dev, dev_docs),
                                test=tagging_utils.sents_to_standoff(y_pred_test, test_docs))
    _save_model_aritfacts(rs, model_dir, y_test, y_pred_test)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", choices=CORPUS_PATH.keys(),
                        help="Corpus identifier.")
    parser.add_argument("run_id", help="Run identifier")
    parser.add_argument("feature_extractor", choices=crf_util.FEATURE_EXTRACTOR.keys(),
                        help="Feature extractor.")
    parser.add_argument("--n_iter", help="Number of random search trials", default=1, type=int)
    parser.add_argument("--n_jobs", help="Number of concurrent jobs", default=1, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    ARGS.run_id = 'crf_' + ARGS.run_id
    logger.add(join(train_utils.model_dir(ARGS.corpus, ARGS.run_id), 'training.log'))
    main(ARGS)
