"""CRF training utilities.

Two feature sets are provided:

   1. Default feature set by sklearn_crfsuite
   2. Liu et al. (2015) features used in de-identification shared task.

Features are encoded in python-crfsuite format:
https://python-crfsuite.readthedocs.io/en/latest/pycrfsuite.html#pycrfsuite.ItemSequence
"""

import re
import string
from typing import Callable, Dict, List, Tuple

import sklearn_crfsuite
from tqdm import tqdm
from unidecode import unidecode

from deidentify.methods.tagging_utils import Token

NEWLINE_REGEX = re.compile(r'\n')
SPACE_REGEX = re.compile(r'\s')


def sent2features(sent: List[Token],
                  feature_extractor: Callable[[List[Token], int], Dict]) -> List[Dict]:
    """Convert a sentence to features in python-crfsuite format.

    python-crfsuite can't handle feature values that contain whitespace or newline characters. These
    characters are replaced with a special #SPACE and #NEWLINE token.

    See issues:
    https://github.com/scrapinghub/python-crfsuite/issues/14
    https://github.com/scrapinghub/python-crfsuite/issues/71

    Parameters
    ----------
    sent : List[Token]
        A sentence constituded of a list of tokens.
    feature_extractor : Callable[[List[Token], int], Dict]
        Callable that represents a token at position `i: int` as a feature dict.

    Returns
    -------
    sent_features : List[Dict]
        List of feature dicts per token. `len(sent_features) == len(sent)`

    """
    sent_features = []

    for i in range(len(sent)):
        token_features = feature_extractor(sent, i)

        for feature_name, value in token_features.items():
            if not isinstance(value, str):
                continue

            value = NEWLINE_REGEX.sub('#NEWLINE', value)
            value = SPACE_REGEX.sub('#SPACE', value)
            token_features[feature_name] = value

        sent_features.append(token_features)

    return sent_features


def sent2labels(sent):
    return [token.label for token in sent]


def sents_to_features_and_labels(sents, feature_extractor):
    X = [sent2features(s, feature_extractor) for s in sents]
    y = [sent2labels(s) for s in sents]
    return X, y


class SentenceFilterCRF(sklearn_crfsuite.CRF):
    """Custom CRF implementation that allows to ignore entire sentences during training/prediction
    time. A default label will be assigned to all tokens within that sentence.

    The confidence of predictions within ignored sentences is set to 1.
    """

    # pylint: disable=too-many-arguments
    # pylint: disable=R0914
    # scikit-learn estimators explicitly have to mention keyword arguments (no *args, **kwargs)
    def __init__(self,
                 ignore_sentence,
                 ignored_label,
                 algorithm=None,
                 min_freq=None,
                 all_possible_states=None,
                 all_possible_transitions=None,
                 c1=None,
                 c2=None,
                 max_iterations=None,
                 num_memories=None,
                 epsilon=None,
                 period=None,
                 delta=None,
                 linesearch=None,
                 max_linesearch=None,
                 calibration_eta=None,
                 calibration_rate=None,
                 calibration_samples=None,
                 calibration_candidates=None,
                 calibration_max_trials=None,
                 pa_type=None,
                 c=None,
                 error_sensitive=None,
                 averaging=None,
                 variance=None,
                 gamma=None,
                 verbose=False,
                 model_filename=None,
                 keep_tempfiles=False,
                 trainer_cls=None):
        self.ignore_sentence = ignore_sentence
        self.ignored_label = ignored_label

        super(SentenceFilterCRF, self).__init__(
            algorithm=algorithm,
            min_freq=min_freq,
            all_possible_states=all_possible_states,
            all_possible_transitions=all_possible_transitions,
            c1=c1,
            c2=c2,
            max_iterations=max_iterations,
            num_memories=num_memories,
            epsilon=epsilon,
            period=period,
            delta=delta,
            linesearch=linesearch,
            max_linesearch=max_linesearch,
            calibration_eta=calibration_eta,
            calibration_rate=calibration_rate,
            calibration_samples=calibration_samples,
            calibration_candidates=calibration_candidates,
            calibration_max_trials=calibration_max_trials,
            pa_type=pa_type,
            c=c,
            error_sensitive=error_sensitive,
            averaging=averaging,
            variance=variance,
            gamma=gamma,
            verbose=verbose,
            model_filename=model_filename,
            keep_tempfiles=keep_tempfiles,
            trainer_cls=trainer_cls)

    def _filter_xy(self, X, y):
        return zip(*filter(lambda xy: not self.ignore_sentence(xy[0]), zip(X, y)))

    def fit(self, X, y, X_dev=None, y_dev=None):
        X, y = self._filter_xy(X, y)

        if X_dev is not None:
            X_dev, y_dev = self._filter_xy(X_dev, y_dev)

        return super(SentenceFilterCRF, self).fit(X, y, X_dev=X_dev, y_dev=y_dev)

    def predict(self, X, verbose=False):
        X = tqdm(X, disable=not verbose, desc='Tag sentences')
        return super().predict(X)

    def predict_single(self, xseq):
        if self.ignore_sentence(xseq):
            return [self.ignored_label] * len(xseq)

        return super().predict_single(xseq)

    def predict_marginals_single(self, xseq):
        if self.ignore_sentence(xseq):
            return [1] * len(xseq)

        return super().predict_marginals_single(xseq)


def sklearn_crfsuite_feature_extractor(sent, i):
    """
    Taken from:
    https://sklearn-crfsuite.readthedocs.io/en/latest/tutorial.html
    """
    word = sent[i].text
    pos_tag = sent[i].pos_tag

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'pos_tag': pos_tag,
        'pos_tag[:2]': pos_tag[:2],
    }
    if i > 0:
        word1 = sent[i - 1].text
        pos_tag1 = sent[i - 1].pos_tag
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
            '-1:pos_tag': pos_tag1,
            '-1:pos_tag[:2]': pos_tag1[:2],
        })
    else:
        features['BOS'] = True

    if i < len(sent) - 1:
        word1 = sent[i + 1].text
        pos_tag1 = sent[i + 1].pos_tag
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
            '+1:pos_tag': pos_tag1,
            '+1:pos_tag[:2]': pos_tag1[:2],
        })
    else:
        features['EOS'] = True

    return features


def liu_feature_extractor(sent, i):
    """Reproduces the features used by Liu et al. (2015).

    Does not include word representation (word2vec, brown clusters) and gazetteer features.

    Reference:
    Liu, Z., et al. (2015). Automatic de-identification of electronic medical records using
    token-level and character-level conditional random fields. Journal of Biomedical Informatics,
    58, S47–S52. https://doi.org/10.1016/J.JBI.2015.06.009
    """
    token = sent[i]

    null_token = Token(text='<PAD>', pos_tag='<PAD>', label='', ner_tag=None)
    sent_window = list_window(sent, center=i, window=(2, 2), oob_item=null_token)
    token_window = [t.text.lower() for t in sent_window]
    pos_window = [t.pos_tag for t in sent_window]
    text_lower = token.text.lower()

    features = {}
    features.update(_ngram_feature_group(token_window, N=1, group_name='bow[-2:2].uni'))
    features.update(_ngram_feature_group(token_window, N=2, group_name='bow[-2:2].bi'))
    features.update(_ngram_feature_group(token_window, N=3, group_name='bow[-2:2].tri'))

    features.update(_ngram_feature_group(pos_window, N=1, group_name='pos[-2:2].uni'))
    features.update(_ngram_feature_group(pos_window, N=2, group_name='pos[-2:2].bi'))
    features.update(_ngram_feature_group(pos_window, N=3, group_name='pos[-2:2].tri'))

    sent_window = list_window(sent, center=i, window=(1, 1), oob_item=null_token)
    pos_window = [t.pos_tag for t in sent_window]
    sep = join_features
    features['bowpos.w0p-1'] = sep((text_lower, pos_window[0]))
    features['bowpos.w0p0'] = sep((text_lower, pos_window[1]))
    features['bowpos.w0p1'] = sep((text_lower, pos_window[2]))
    features['bowpos.w0p-1p0'] = sep((text_lower, pos_window[0], pos_window[1]))
    features['bowpos.w0p0p1'] = sep((text_lower, pos_window[1], pos_window[2]))
    features['bowpos.w0p-1p1'] = sep((text_lower, pos_window[0], pos_window[2]))
    features['bowpos.w0p-1p0p1'] = sep((text_lower, pos_window[0], pos_window[1], pos_window[2]))

    features['sent.len(sent)'] = len(sent)
    features['sent.end_mark'] = sent[-1].text.strip() in ['!', '?', '.']
    features['sent.has_unmatched_bracket'] = has_unmatched_bracket(sent)

    for j in range(1, 6):
        features['suffix[-{}:]'.format(j)] = text_lower[-j:]
        features['prefix[:{}]'.format(j)] = text_lower[:j]

    features['word.isupper()'] = token.text.isupper()
    features['word.istitle()'] = token.text.istitle()
    features['word.isdigit()'] = token.text.isdigit()
    features['word.contains_digit'] = any(c.isdigit() for c in token.text)
    features['word.has_upper_inside'] = any(c.isupper() for c in token.text[1:])
    features['word.has_punct_inside'] = any(c in string.punctuation for c in token.text[1:])
    features['word.has_digit_inside'] = any(c.isdigit() for c in token.text[1:])
    features['word.is_ascii'] = all(ord(c) < 128 for c in token.text)
    features['word.ner_tag'] = token.ner_tag
    features['word.pos_tag'] = token.pos_tag

    shape = word_shape(token.text)
    features['shape.long'] = shape
    features['shape.short'] = collapse_word_shape(shape)

    return features


def join_features(feature_list):
    return '|'.join(feature_list)


def ngrams(tokens, N):
    return [tuple(tokens[i:i + N]) for i in range(len(tokens) - N + 1)]


def list_window(sent: List, center: int, window: Tuple[int, int], oob_item=None) -> List:
    """Get a window of tokens within a sentence.

    Parameters
    ----------
    sent : List
        A list of tokens.
    center : int
        The index acting as center of the window.
    window : Tuple[int, int]
        The window width. `window[0]` is elements before center, `window[1]` is elements after
        center. Interval is closed.
    oob_item : type
        The item to return if window indexes are out of bounds of `sent`.

    Returns
    -------
    tokens : List
        The tokens within the given window.

    """
    tokens = []
    for i in range(center - window[0], center + window[1] + 1):
        if i < 0:
            tokens.append(oob_item)
        elif i >= len(sent):
            tokens.append(oob_item)
        else:
            tokens.append(sent[i])
    return tokens


def _ngram_feature_group(tokens, N, group_name, sep=join_features):
    features = {}
    token_ngrams = ngrams(tokens, N)
    for j, item in enumerate(token_ngrams):
        features['{}.{}'.format(group_name, j)] = sep(item)
    return features


def has_unmatched_bracket(sent):
    n_open = 0

    for token in sent:
        if token.text == '(':
            n_open += 1
        elif token.text == ')':
            n_open -= 1

    return n_open > 0


def word_shape(token):
    shape = ''
    for c in unidecode(token):
        if c in string.ascii_lowercase:
            shape += 'a'
        elif c in string.ascii_uppercase:
            shape += 'A'
        elif c in string.digits:
            shape += '#'
        else:
            shape += '-'
    return shape


def collapse_word_shape(shape):
    collapsed = ''
    current = None
    for c in shape:
        if c == current:
            continue
        collapsed += c
        current = c
    return collapsed
