from deidentify.surrogates.generators import IDSurrogates

from .util import RandomDataMock


def test_replace_ids():
    surrogate_generator = IDSurrogates(annotations=[], random_data=RandomDataMock())

    assert surrogate_generator.replace_one('DE951') == 'CC111'
    assert surrogate_generator.replace_one('ef-51m@') == 'cc-11c@'
    assert surrogate_generator.replace_one('123456') == '111111'
