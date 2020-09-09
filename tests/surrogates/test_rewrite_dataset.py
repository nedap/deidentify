import argparse
import filecmp
import glob
from os.path import basename, dirname, join

import pytest

from deidentify.base import Annotation
from deidentify.surrogates import rewrite_dataset


def test_apply_surrogates():
    text = 'ccc cc ccc c c ccc cccccc cccc'
    annotations = [
        Annotation('ccc', start=0, end=3, tag='A'),
        Annotation('cc', start=4, end=6, tag='A'),
        Annotation('ccc', start=15, end=18, tag='B')
    ]
    surrogates = ['a', 'dd', 'bbbbb']

    surrogate_doc = rewrite_dataset.apply_surrogates(text, annotations, surrogates)
    assert surrogate_doc.text == 'a dd ccc c c bbbbb cccccc cccc'
    assert surrogate_doc.annotations == [
        Annotation('a', start=0, end=1, tag='A'),
        Annotation('dd', start=2, end=4, tag='A'),
        Annotation('bbbbb', start=13, end=18, tag='B')
    ]
    assert surrogate_doc.annotations_without_surrogates == []


def test_apply_surrogates_no_annotations():
    surrogate_doc = rewrite_dataset.apply_surrogates('ccc cc ccc', annotations=[], surrogates=[])
    assert surrogate_doc.text == 'ccc cc ccc'
    assert surrogate_doc.annotations == []
    assert surrogate_doc.annotations_without_surrogates == []


def test_apply_surrogates_errors_raise():
    text = 'ccc cc ccc'
    annotations = [
        Annotation('ccc', start=0, end=3, tag='A'),
        Annotation('cc', start=4, end=6, tag='A'),
        Annotation('ccc', start=7, end=10, tag='B')
    ]
    surrogates = ['a', None, 'b']

    with pytest.raises(ValueError):
        rewrite_dataset.apply_surrogates(text, annotations, surrogates)

    with pytest.raises(ValueError):
        rewrite_dataset.apply_surrogates(text, annotations, surrogates, errors='raise')


def test_apply_surrogates_errors_ignore():
    text = 'ccc cc ccc'
    annotations = [
        Annotation('ccc', start=0, end=3, tag='A'),
        Annotation('cc', start=4, end=6, tag='A'),
        Annotation('ccc', start=7, end=10, tag='B')
    ]
    surrogates = ['a', None, 'b']

    surrogate_doc = rewrite_dataset.apply_surrogates(text, annotations, surrogates, errors='ignore')
    assert surrogate_doc.text == 'a cc b'
    assert surrogate_doc.annotations == [
        Annotation('a', start=0, end=1, tag='A'),
        Annotation('cc', start=2, end=4, tag='A'),
        Annotation('b', start=5, end=6, tag='B')
    ]
    assert surrogate_doc.annotations_without_surrogates == [
        Annotation('cc', start=4, end=6, tag='A'),
    ]


def test_apply_surrogates_errors_coerce():
    text = 'ccc cc ccc'
    annotations = [
        Annotation('ccc', start=0, end=3, tag='A'),
        Annotation('cc', start=4, end=6, tag='A'),
        Annotation('ccc', start=7, end=10, tag='B')
    ]
    surrogates = ['a', None, 'b']

    surrogate_doc = rewrite_dataset.apply_surrogates(text, annotations, surrogates, errors='coerce')
    assert surrogate_doc.text == 'a [A] b'
    assert surrogate_doc.annotations == [
        Annotation('a', start=0, end=1, tag='A'),
        Annotation('[A]', start=2, end=5, tag='A'),
        Annotation('b', start=6, end=7, tag='B')
    ]
    assert surrogate_doc.annotations_without_surrogates == [
        Annotation('cc', start=4, end=6, tag='A'),
    ]


def test_main(tmpdir):
    args = argparse.Namespace(
        surrogate_table=join(dirname(__file__), 'data/annotations-rewrite-table.csv'),
        data_path=join(dirname(__file__), 'data/original'),
        output_path=tmpdir
    )

    ann_files = glob.glob(join(dirname(__file__), 'data/rewritten/*.ann'))
    txt_files = glob.glob(join(dirname(__file__), 'data/rewritten/*.txt'))
    to_compare = ann_files + txt_files
    to_compare = [basename(f) for f in to_compare]

    rewrite_dataset.main(args)

    for file in to_compare:
        expected = join(dirname(__file__), 'data/rewritten/', file)
        actual = join(tmpdir, file)
        assert filecmp.cmp(expected, actual)
