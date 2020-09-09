import argparse
import filecmp
from os.path import dirname, join, basename

import glob

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

    result = rewrite_dataset.apply_surrogates(text, annotations, surrogates)
    text_rewritten, adjusted_annotations = result
    assert text_rewritten == 'a dd ccc c c bbbbb cccccc cccc'
    assert adjusted_annotations == [
        Annotation('a', start=0, end=1, tag='A'),
        Annotation('dd', start=2, end=4, tag='A'),
        Annotation('bbbbb', start=13, end=18, tag='B')
    ]


def test_apply_surrogates_no_annotations():
    result = rewrite_dataset.apply_surrogates('ccc cc ccc', annotations=[], surrogates=[])
    text_rewritten, adjusted_annotations = result
    assert text_rewritten == 'ccc cc ccc'
    assert adjusted_annotations == []


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
