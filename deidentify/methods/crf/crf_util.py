import operator
import pickle
from collections import Counter
from os.path import join

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from sklearn_crfsuite import metrics

from deidentify.methods.crf import crf_labeler


def meta_sentence_filter_sklearn_crfsuite(sent):
    return sent[0]['word.lower()'].startswith('===')


def meta_sentence_filter_liu(sent):
    return sent[0]['prefix[:3]'].startswith('===')


FEATURE_EXTRACTOR = {
    'sklearn_crfsuite': (crf_labeler.sklearn_crfsuite_feature_extractor,
                         meta_sentence_filter_sklearn_crfsuite),
    'liu_2015': (crf_labeler.liu_feature_extractor, meta_sentence_filter_liu)
}


def save_bio_report(y_true, y_pred, labels, out_dir):
    sorted_labels = sorted(
        labels,
        key=lambda name: (name[1:], name[0])
    )

    report = metrics.flat_classification_report(y_true, y_pred, labels=sorted_labels, digits=3)
    with open(join(out_dir, 'bio_classification_report.txt'), 'w') as text_file:
        print(report, file=text_file)


def save_transition_features(crf, out_dir):
    transitions_counter = Counter(crf.transition_features_)

    with open(join(out_dir, 'transition_features.txt'), 'w') as text_file:
        print("Top likely transitions (N=20):", file=text_file)
        _print_transitions(transitions_counter.most_common(20), text_file)

        print("\nTop unlikely transitions (N=20):", file=text_file)
        _print_transitions(transitions_counter.most_common()[-20:], text_file)

        print("\nAll transitions (N={}):".format(len(transitions_counter)), file=text_file)
        _print_transitions(transitions_counter.most_common(), text_file)


def save_state_features(crf, out_dir):
    state_features_counter = Counter(crf.state_features_)

    with open(join(out_dir, 'state_features.txt'), 'w') as text_file:
        print("Top positive:", file=text_file)
        _print_state_features(state_features_counter.most_common(30), text_file)

        print("\nTop negative:", file=text_file)
        _print_state_features(state_features_counter.most_common()[-30:], text_file)


def persist_model(crf, out_dir):
    with open(join(out_dir, 'model.pickle'), 'wb') as file:
        pickle.dump(crf, file)


def _print_transitions(trans_features, file):
    for (label_from, label_to), weight in trans_features:
        print("{:>25} -> {:<26} {:.4f}".format(label_from, label_to, weight), file=file)


def _print_state_features(state_features, file):
    for (attr, label), weight in state_features:
        print("{:.4f} {:<25} {}".format(weight, label, attr), file=file)


def plot_random_search_parameter_pair(out_file, cv_results, param_x, param_y, title=None):
    _x = [run[param_x] for run in cv_results['params']]
    _y = [run[param_y] for run in cv_results['params']]
    _c = cv_results['mean_test_score']

    fig = plt.figure()
    ax = plt.gca()
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_xlabel(param_x)
    ax.set_ylabel(param_y)

    if not title:
        title = "Random Search Results\n(min={:0.3}, max={:0.3})".format(min(_c), max(_c))
    plt.title(title, loc='left')

    sc = ax.scatter(_x, _y, c=_c, s=25, alpha=0.9, edgecolor='black', cmap='YlGnBu')
    ix, _ = max(enumerate(_c), key=operator.itemgetter(1))
    plt.scatter(_x[ix], _y[ix], c='r', marker='*', s=40)

    plt.colorbar(sc)
    ax.set_axisbelow(True)
    plt.grid()

    with PdfPages(out_file) as pdf:
        pdf.savefig(fig, bbox_inches='tight')


def save_rs_results(rs_results, model_dir):
    pd.DataFrame(rs_results).to_json(join(model_dir, 'rs_results.json'))
