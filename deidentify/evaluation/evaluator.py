from collections import namedtuple
from typing import List

import numpy as np
import spacy
from loguru import logger
from sklearn.metrics import confusion_matrix
from spacy.gold import biluo_tags_from_offsets

from deidentify.base import Document
from deidentify.evaluation.metric import Metric

Entity = namedtuple('Entity', ['doc_name', 'start', 'end', 'tag'])
ENTITY_TAG = 'ENT'


def flatten(lists):
    return [e for l in lists for e in l]


class Evaluator:

    def __init__(self, gold: List[Document], predicted: List[Document], language='nl',
                 tokenizer=None):
        self.gold = gold
        self.predicted = predicted

        self.tags = sorted(list(set(ann.tag for doc in gold for ann in doc.annotations)))

        if tokenizer:
            self.tokenize = tokenizer
        else:
            if language not in self.supported_languages():
                logger.warning(
                    'Unknown language {} for evaluation. Fallback to "en"'.format(language))
                language = 'en'

            if language == 'nl':
                self.tokenize = spacy.load('nl_core_news_sm')
            else:
                self.tokenize = spacy.load('en_core_web_sm')

    @staticmethod
    def supported_languages():
        return ('nl', 'en')

    def entity_level(self):
        metric = Metric('entity level')

        entities_gold = set(Entity(doc.name, ann.start, ann.end, ann.tag)
                            for doc in self.gold for ann in doc.annotations)
        entities_pred = set(Entity(doc.name, ann.start, ann.end, ann.tag)
                            for doc in self.predicted for ann in doc.annotations)

        for pred in entities_pred:
            if pred in entities_gold:
                metric.add_tp(class_name=pred.tag)
            else:
                metric.add_fp(class_name=pred.tag)

        for gold in entities_gold:
            if gold not in entities_pred:
                metric.add_fn(class_name=gold.tag)
            else:
                # true negatives are not defined in an entity-level evaluation
                pass

        return metric

    def token_level(self):
        metric = Metric('token level')

        tags_gold = flatten(self.token_annotations(doc) for doc in self.gold)
        tags_pred = flatten(self.token_annotations(doc) for doc in self.predicted)

        cm = confusion_matrix(tags_gold, tags_pred, labels=self.tags + ['O'])

        row_sum, col_sum, cm_sum = np.sum(cm, axis=0), np.sum(cm, axis=1), np.sum(cm)
        for i, tag in enumerate(self.tags):
            tp = cm[i, i]
            fp = row_sum[i] - cm[i, i]
            fn = col_sum[i] - cm[i, i]
            tn = cm_sum - tp - fp - fn

            metric.add_tp(class_name=tag, N=tp)
            metric.add_fp(class_name=tag, N=fp)
            metric.add_fn(class_name=tag, N=fn)
            metric.add_tn(class_name=tag, N=tn)

        return metric

    def token_level_blind(self):
        metric = Metric('token (blind)')

        tags_gold = flatten(self.token_annotations(doc, tag_blind=True) for doc in self.gold)
        tags_pred = flatten(self.token_annotations(doc, tag_blind=True) for doc in self.predicted)
        # convert labels: ENT => 1, else => 0
        tags_gold = list(map(lambda tag: int(tag == ENTITY_TAG), tags_gold))
        tags_pred = list(map(lambda tag: int(tag == ENTITY_TAG), tags_pred))

        tn, fp, fn, tp = confusion_matrix(tags_gold, tags_pred).ravel()

        metric.add_tp(class_name=ENTITY_TAG, N=tp)
        metric.add_fp(class_name=ENTITY_TAG, N=fp)
        metric.add_fn(class_name=ENTITY_TAG, N=fn)
        metric.add_tn(class_name=ENTITY_TAG, N=tn)

        return metric

    def token_annotations(self, doc, tag_blind=False, entity_tag=ENTITY_TAG):
        parsed = self.tokenize(doc.text, disable=("tagger", "parser", "ner"))
        entities = [(int(ann.start), int(ann.end), ann.tag) for ann in doc.annotations]
        biluo_tags = biluo_tags_from_offsets(parsed, entities)

        tags = []
        for tag in biluo_tags:
            if tag == "O":
                tags.append('O')
            elif tag == '-':
                # Returned by spacy if token boundaries mismatch entity boundaries.
                # These errors are ignored.
                #
                # https://spacy.io/api/goldparse#biluo_tags_from_offsets
                tags.append('O')
            elif tag_blind:
                tags.append(entity_tag)
            else:
                tags.append(tag[2:])

        return tags
