from deidentify.methods.crf.crf_labeler import (Token, collapse_word_shape,
                                                has_unmatched_bracket,
                                                list_window,
                                                liu_feature_extractor, ngrams,
                                                word_shape)


def test_list_window():
    sent = ['a', 'b', 'w', 'c', 'd']

    assert list_window(sent, center=2, window=(0, 0)) == ['w']
    assert list_window(sent, center=2, window=(1, 1)) == ['b', 'w', 'c']
    assert list_window(sent, center=2, window=(2, 2)) == ['a', 'b', 'w', 'c', 'd']
    assert list_window(sent, center=2, window=(3, 3)) == [None, 'a', 'b', 'w', 'c', 'd', None]
    assert list_window(sent, center=0, window=(3, 3)) == [None, None, None, 'a', 'b', 'w', 'c']
    assert list_window(sent, center=0, window=(3, 0)) == [None, None, None, 'a']


def test_ngrams():
    tokens = ['a', 'b', 'w', 'c', 'd']
    assert ngrams(tokens, N=1) == [('a',), ('b',), ('w',), ('c',), ('d',)]
    assert ngrams(tokens, N=2) == [('a', 'b'), ('b', 'w'), ('w', 'c'), ('c', 'd')]
    assert ngrams(tokens, N=3) == [('a', 'b', 'w'), ('b', 'w', 'c'), ('w', 'c', 'd')]


def test_unmatched_bracket():
    sentence = [
        Token(text='De', pos_tag='DET', label='O', ner_tag=None),
        Token(text='patient', pos_tag='NOUN', label='O', ner_tag=None),
        Token(text='Ingmar', pos_tag='NOUN', label='O', ner_tag=None),
        Token(text='Koopal', pos_tag='PROPN', label='O', ner_tag=None),
        Token(text='(', pos_tag='PUNCT', label='O', ner_tag=None),
    ]

    assert has_unmatched_bracket(sentence)
    sentence.append(Token(text=')', pos_tag='PUNCT', label='O', ner_tag=None))
    assert not has_unmatched_bracket(sentence)


def test_word_shape():
    assert word_shape('IngmAr-12a') == 'AaaaAa-##a'
    assert word_shape('1234') == '####'
    assert word_shape('ömar') == 'aaaa'


def test_collapse_word_shape():
    assert collapse_word_shape('AaaaAa-##a') == 'AaAa-#a'
    assert collapse_word_shape('####') == '#'


def test_liu_feature_extractor():
    sentence = [
        Token(text='De', pos_tag='DET', label='O', ner_tag=None),
        Token(text='patient', pos_tag='NOUN', label='O', ner_tag=None),
        Token(text='Ingmar', pos_tag='NOUN', label='O', ner_tag='PER'),
        Token(text='Koopal', pos_tag='PROPN', label='O', ner_tag='PER'),
        Token(text='(', pos_tag='PUNCT', label='O', ner_tag=None),
        Token(text='t', pos_tag='NOUN', label='O', ner_tag=None),
        Token(text=':', pos_tag='PUNCT', label='O', ner_tag=None),
        Token(text='06', pos_tag='NUM', label='O', ner_tag=None),
        Token(text='-', pos_tag='PUNCT', label='O', ner_tag=None),
        Token(text='16769063', pos_tag='NUM', label='O', ner_tag=None),
        Token(text=')', pos_tag='PUNCT', label='O', ner_tag=None),
    ]

    # from pprint import pprint
    # pprint(liu_feature_extractor(sentence, 2))

    assert liu_feature_extractor(sentence, 2) == {
        'bow[-2:2].uni.0': 'de',
        'bow[-2:2].uni.1': 'patient',
        'bow[-2:2].uni.2': 'ingmar',
        'bow[-2:2].uni.3': 'koopal',
        'bow[-2:2].uni.4': '(',
        'bow[-2:2].bi.0': 'de|patient',
        'bow[-2:2].bi.1':  'patient|ingmar',
        'bow[-2:2].bi.2':  'ingmar|koopal',
        'bow[-2:2].bi.3':  'koopal|(',
        'bow[-2:2].tri.0': 'de|patient|ingmar',
        'bow[-2:2].tri.1': 'patient|ingmar|koopal',
        'bow[-2:2].tri.2': 'ingmar|koopal|(',
        'pos[-2:2].uni.0': 'DET',
        'pos[-2:2].uni.1': 'NOUN',
        'pos[-2:2].uni.2': 'NOUN',
        'pos[-2:2].uni.3': 'PROPN',
        'pos[-2:2].uni.4': 'PUNCT',
        'pos[-2:2].bi.0':  'DET|NOUN',
        'pos[-2:2].bi.1':  'NOUN|NOUN',
        'pos[-2:2].bi.2':  'NOUN|PROPN',
        'pos[-2:2].bi.3':  'PROPN|PUNCT',
        'pos[-2:2].tri.0': 'DET|NOUN|NOUN',
        'pos[-2:2].tri.1': 'NOUN|NOUN|PROPN',
        'pos[-2:2].tri.2': 'NOUN|PROPN|PUNCT',
        'bowpos.w0p-1': 'ingmar|NOUN',
        'bowpos.w0p-1p0': 'ingmar|NOUN|NOUN',
        'bowpos.w0p-1p0p1': 'ingmar|NOUN|NOUN|PROPN',
        'bowpos.w0p-1p1': 'ingmar|NOUN|PROPN',
        'bowpos.w0p0': 'ingmar|NOUN',
        'bowpos.w0p0p1': 'ingmar|NOUN|PROPN',
        'bowpos.w0p1': 'ingmar|PROPN',
        'sent.end_mark': False,
        'sent.len(sent)': 11,
        'sent.has_unmatched_bracket': False,
        'prefix[:1]': 'i',
        'prefix[:2]': 'in',
        'prefix[:3]': 'ing',
        'prefix[:4]': 'ingm',
        'prefix[:5]': 'ingma',
        'suffix[-1:]': 'r',
        'suffix[-2:]': 'ar',
        'suffix[-3:]': 'mar',
        'suffix[-4:]': 'gmar',
        'suffix[-5:]': 'ngmar',

        'word.contains_digit': False,
        'word.has_digit_inside': False,
        'word.has_punct_inside': False,
        'word.has_upper_inside': False,
        'word.is_ascii': True,
        'word.isdigit()': False,
        'word.istitle()': True,
        'word.isupper()': False,
        'word.ner_tag': 'PER',
        'word.pos_tag': 'NOUN',

        'shape.long': 'Aaaaaa',
        'shape.short': 'Aa',
    }


if __name__ == '__main__':
    test_liu_feature_extractor()
