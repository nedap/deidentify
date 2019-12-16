import pytest

from deidentify.surrogates.generators import (DIAL_CODES_BY_LENGTH, PhoneFaxSurrogates,
                                   RandomData)


def test_mask_phonenumber():
    pfs = PhoneFaxSurrogates(annotations=[])

    assert pfs.mask_phonenumber('(026) 123 456 7') == '(0DD) ### ### #'
    assert pfs.mask_phonenumber('026 - 123 456 7') == '0DD - ### ### #'
    assert pfs.mask_phonenumber('026- 123 456 7') == '0DD- ### ### #'
    assert pfs.mask_phonenumber('026 -123 456 7') == '0DD -### ### #'
    assert pfs.mask_phonenumber('0261234567') == '0DD#######'
    assert pfs.mask_phonenumber('123 456 7') == '### ### #'
    assert pfs.mask_phonenumber('+31 512 456 789') == '+CC DDD ### ###'
    assert pfs.mask_phonenumber('+31 6 11 22 11 11') == '+CC D ## ## ## ##'
    assert pfs.mask_phonenumber('+31 (0) 6 11 22 11 11') == '+CC (0) D ## ## ## ##'
    assert pfs.mask_phonenumber('0031 6 11 22 11 11') == '00CC D ## ## ## ##'


def test_mask_phonenumber_invalid():
    pfs = PhoneFaxSurrogates(annotations=[])

    with pytest.raises(ValueError):
        pfs.mask_phonenumber('abcdf')

    with pytest.raises(ValueError):
        pfs.mask_phonenumber('123456')


def test_replace_pattern():
    pfs = PhoneFaxSurrogates(annotations=[], random_data=RandomData(seed=42))

    for _ in range(100):
        pattern = '(0DD) ### ### #'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[2:4] in DIAL_CODES_BY_LENGTH[2]
        assert replacement[6] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '0DD - ### ### #'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[1:3] in DIAL_CODES_BY_LENGTH[2]
        assert replacement[6] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '0DD- ### ### #'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[1:3] in DIAL_CODES_BY_LENGTH[2]
        assert replacement[5] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '0DD#######'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[1:3] in DIAL_CODES_BY_LENGTH[2]
        assert replacement[3] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '### ### #'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[0] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '+CC DDD ### ###'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[0] == '+'
        assert replacement[1:3] == '31'
        assert replacement[4:7] in DIAL_CODES_BY_LENGTH[3]
        assert replacement[8] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '+CC D ## ## ## ##'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[0] == '+'
        assert replacement[1:3] == '31'
        assert replacement[4] == '6'  # mobile phone
        assert replacement[6] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '00CC D ## ## ## ##'
        replacement = pfs.replace_pattern(pattern)
        assert replacement[0:2] == '00'
        assert replacement[2:4] == '31'
        assert replacement[5] == '6'  # mobile phone
        assert replacement[7] in '123456789'
        assert len(replacement) == len(pattern)


def test_replace_phonenumber():
    pfs = PhoneFaxSurrogates(annotations=[], random_data=RandomData(seed=42))

    for _ in range(100):
        pattern = '(026) 123 456 7'
        replacement = pfs.replace_one(pattern)
        assert replacement[2:4] in DIAL_CODES_BY_LENGTH[2]
        assert replacement[6] in '123456789'
        assert len(replacement) == len(pattern)

        pattern = '+31 (0) 6 11 22 11 11'
        replacement = pfs.replace_one(pattern)
        assert replacement[0] == '+'
        assert replacement[1:3] == '31'
        assert replacement[3:8] == ' (0) '
        assert replacement[8] == '6'  # mobile phone
        assert replacement[10] in '123456789'
        assert len(replacement) == len(pattern)
