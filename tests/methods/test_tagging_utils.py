from deidentify.methods.tagging_utils import (ParsedDoc, _bio_to_biluo,
                                              _group_sentences,
                                              fix_dangling_entities)


def test_group_sentences():
    tags = [['O', 'O'], ['B', 'B'], ['B', 'I']]
    docs = [
        ParsedDoc(spacy_doc=None, name='doc_a', text=''),
        ParsedDoc(spacy_doc=None, name='doc_a', text=''),
        ParsedDoc(spacy_doc=None, name='doc_b', text='')]

    output = _group_sentences(tags, docs)
    assert output == [
        (ParsedDoc(spacy_doc=None, name='doc_a', text=''), ['O', 'O', 'B', 'B']),
        (ParsedDoc(spacy_doc=None, name='doc_b', text=''), ['B', 'I'])
    ]


def test_bio_to_biluo():
    bio_tags = ['B-a', 'B-b', 'O', 'B-b', 'I-b', 'I-b', 'O', 'O', 'O', 'B-a', 'I-a']
    assert _bio_to_biluo(bio_tags) == [
        'U-a', 'U-b', 'O', 'B-b', 'I-b', 'L-b', 'O', 'O', 'O', 'B-a', 'L-a']

    bio_tags = ['B-a']
    assert _bio_to_biluo(bio_tags) == ['U-a']

    bio_tags = ['B-a', 'B-a']
    assert _bio_to_biluo(bio_tags) == ['U-a', 'U-a']

    bio_tags = ['B-a', 'B-a', 'I-a']
    assert _bio_to_biluo(bio_tags) == ['U-a', 'B-a', 'L-a']

    bio_tags = ['B-a', 'O']
    assert _bio_to_biluo(bio_tags) == ['U-a', 'O']

    bio_tags = ['B-a', 'I-a']
    assert _bio_to_biluo(bio_tags) == ['B-a', 'L-a']

    bio_tags = ['O', 'O', 'O', 'B-a']
    assert _bio_to_biluo(bio_tags) == ['O', 'O', 'O', 'U-a']


def test_fix_dangling_entities():
    assert fix_dangling_entities(['I-a']) == ['B-a']
    assert fix_dangling_entities(['O', 'I-a']) == ['O', 'B-a']
    assert fix_dangling_entities(['I-a', 'O']) == ['B-a', 'O']
    assert fix_dangling_entities(['I-a', 'I-b']) == ['B-a', 'B-b']
    assert fix_dangling_entities(['B-a', 'I-b']) == ['B-a', 'B-b']
    assert fix_dangling_entities(['I-b', 'B-b', 'I-b']) == ['B-b', 'B-b', 'I-b']

    bio_tags = ['O', 'I-a', 'I-a', 'O', 'I-b', 'O', 'O', 'B-a', 'I-a', 'I-b']
    fixed = ['O', 'B-a', 'I-a', 'O', 'B-b', 'O', 'O', 'B-a', 'I-a', 'B-b']
    assert fix_dangling_entities(bio_tags) == fixed
