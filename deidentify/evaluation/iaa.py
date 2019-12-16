import glob
from os.path import join
from typing import List

import numpy as np

from deidentify.base import Annotation
from deidentify.dataset.brat import load_brat_annotations


def load_annotations(path):
    annotations = []
    for ann_file in glob.glob(join(path, '*.ann')):
        annotations += load_brat_annotations(ann_file)

    return annotations


def precision(correct, actual):
    if actual == 0:
        return 0

    return correct / actual


def recall(correct, possible):
    if possible == 0:
        return 0

    return correct / possible


def f1(p, r):
    if p + r == 0:
        return 0

    return 2 * (p * r) / (p + r)


def annotation_set(annotations, tag_name=None):
    if tag_name:
        annotations = [a for a in annotations if a.tag == tag_name]
    return set(annotations)


def annotator_agreement(annotations_a: List[Annotation],
                        annotations_b: List[Annotation], tag_name=None):
    annotations_a = annotation_set(annotations_a, tag_name)
    annotations_b = annotation_set(annotations_b, tag_name)

    correct = len(annotations_a & annotations_b)
    positive = len(annotations_a)
    predicted = len(annotations_b)

    if positive <= 0:
        return np.NaN

    p = precision(correct, predicted)
    r = recall(correct, positive)
    return f1(p, r)
