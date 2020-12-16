from pathlib import Path
from unittest.mock import patch

import pytest

from deidentify.taggers.base import cached_model_file, lookup_model


def test_cached_model_file(tmpdir):
    p = tmpdir.mkdir('model_bilstmcrf_a').join('final-model.pt')
    p.write('')

    p = tmpdir.mkdir('model_crf_b').join('model.pickle')
    p.write('')

    with patch('deidentify.cache_root', Path(tmpdir)):
        assert cached_model_file('model_bilstmcrf_a') \
            == Path(tmpdir, 'model_bilstmcrf_a', 'final-model.pt')
        assert cached_model_file('model_crf_b') \
            == Path(tmpdir, 'model_crf_b', 'model.pickle')


def test_cached_model_file_raises_error_on_missing_model(tmpdir):
    with patch('deidentify.cache_root', Path(tmpdir)):
        # cache is empty
        with pytest.raises(ValueError):
            cached_model_file('model_bilstmcrf_a')

        # cache has model dir, but not model file
        model_dir = tmpdir.mkdir('model_bilstmcrf_a')
        with pytest.raises(ValueError):
            cached_model_file('model_bilstmcrf_a')

        # cache is complete
        model_dir.join('final-model.pt').write('')
        assert cached_model_file('model_bilstmcrf_a') \
            == Path(tmpdir, 'model_bilstmcrf_a', 'final-model.pt')


def test_lookup_model_with_invalid_name_raises_value_error():
    with pytest.raises(ValueError):
        lookup_model('invalid')
