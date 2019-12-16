import argparse
import itertools
import os
from os.path import join

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.metrics import make_scorer
from sklearn.model_selection import learning_curve
from sklearn.utils import parallel_backend
from sklearn_crfsuite.metrics import flat_f1_score

from deidentify.methods import train_utils
from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.methods import tagging_utils
from deidentify.methods.crf import crf_labeler, crf_util
from deidentify.tokenizer import TokenizerFactory


def plot_learning_curve(estimator, title, X, y, out_dir, ylim=None, cv=None,
                        n_jobs=None, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and training learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross-validation,
          - integer, to specify the number of folds.
          - :term:`CV splitter`,
          - An iterable yielding (train, test) splits as arrays of indices.

        For integer/None inputs, if ``y`` is binary or multiclass,
        :class:`StratifiedKFold` used. If the estimator is not a classifier
        or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validators that can be used here.

    n_jobs : int or None, optional (default=None)
        Number of jobs to run in parallel.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    train_sizes : array-like, shape (n_ticks,), dtype float or int
        Relative or absolute numbers of training examples that will be used to
        generate the learning curve. If the dtype is float, it is regarded as a
        fraction of the maximum size of the training set (that is determined
        by the selected validation method), i.e. it has to be within (0, 1].
        Otherwise it is interpreted as absolute sizes of the training sets.
        Note that for classification the number of samples usually have to
        be big enough to contain at least one sample from each class.
        (default: np.linspace(0.1, 1.0, 5))
    """
    fig = plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training sentences")
    plt.ylabel("Token-level F1 score (micro)")

    labels = list(set(label for sent in y for label in sent))
    labels.remove('O')
    logger.info('Labels: {}'.format(labels))

    scorer = make_scorer(flat_f1_score, labels=labels, average='micro')

    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes, scoring=scorer, verbose=1)

    logger.info('Draw plot...')
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.grid()
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")

    with PdfPages(join(out_dir, 'learning_curve.pdf')) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    plt.savefig(join(out_dir, 'learning_curve.png'))


def main(args):
    logger.info('Args = {}'.format(args))
    corpus = CorpusLoader().load_corpus(CORPUS_PATH[args.corpus])
    tokenizer = TokenizerFactory().tokenizer(args.corpus)
    logger.info('Loaded corpus: {}'.format(corpus))

    model_dir = train_utils.model_dir(corpus.name, args.run_id)
    os.makedirs(model_dir, exist_ok=True)

    logger.info('Get sentences...')
    docs = list(itertools.chain(corpus.train, corpus.dev))
    sents, _ = tagging_utils.standoff_to_sents(docs, tokenizer, verbose=True)

    logger.info('Compute features...')
    feature_extractor, meta_sentence_filter = crf_util.FEATURE_EXTRACTOR[args.feature_extractor]
    X, y = crf_labeler.sents_to_features_and_labels(sents, feature_extractor)

    logger.info('len(X) = {}'.format(len(X)))
    logger.info('len(y) = {}'.format(len(y)))

    crf = crf_labeler.SentenceFilterCRF(
        ignore_sentence=meta_sentence_filter,
        ignored_label='O',
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )

    logger.info('Start learing curve computation...')
    with parallel_backend('multiprocessing'):
        # scikit-learn changed the default multiprocessing to 'loky' in 0.21. It appears that this
        # is not supported by sklearn_crfsuite. Therefore, we switch to the legacy 'multiprocessing'
        # parallel backend.
        plot_learning_curve(crf, 'CRF learning curve (sentences: N={})'.format(len(X)),
                            X, y, out_dir=model_dir, cv=5, n_jobs=12)
    logger.info('Done...')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", choices=CORPUS_PATH.keys(), help="Corpus identifier.")
    parser.add_argument("run_id", help="Run identifier")
    parser.add_argument("feature_extractor", choices=crf_util.FEATURE_EXTRACTOR.keys(),
                        help="Feature extractor.")
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    ARGS.run_id = 'crf_' + ARGS.run_id
    logger.add(join(train_utils.model_dir(ARGS.corpus, ARGS.run_id), 'learning-curve.log'))
    main(ARGS)
