import argparse
import filecmp
from os.path import dirname, join

from deidentify.surrogates import generate_surrogates


def test_generate_surrogates(tmpdir):
    dataset_path = join(dirname(__file__), 'data/original')
    expected = join(dirname(__file__), 'data/annotations-rewrite-table.csv')
    actual = join(tmpdir, 'surrogates.actual.csv')

    args = argparse.Namespace(dataset_path=dataset_path, output_file=actual)
    generate_surrogates.main(args)
    assert filecmp.cmp(expected, actual)
