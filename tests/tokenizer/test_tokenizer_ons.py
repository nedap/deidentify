from deidentify.tokenizer.tokenizer_ons import TokenizerOns

tokenizer = TokenizerOns()


def test_tokenizer():
    text = '=== Answer: 1234 ===\ntest a b c d.\n=== Report: 1234 ===\nMw. test test test'
    doc = tokenizer.parse_text(text)

    tokens = [t.text for t in doc]

    assert tokens == [
        '=== Answer: 1234 ===\n', 'test', 'a', 'b', 'c', 'd.', '\n', '=== Report: 1234 ===\n',
        'Mw.', 'test', 'test', 'test'
    ]


def test_sentence_segmentation():
    text = '=== Answer: 1234 ===\nDit is een zin.\n=== Report: 1234 ===\nMw. heeft goed gegeten.'
    doc = tokenizer.parse_text(text)
    sents = [sent.text for sent in doc.sents]

    assert sents == [
        '=== Answer: 1234 ===\n',
        'Dit is een zin.\n',
        '=== Report: 1234 ===\n',
        'Mw. heeft goed gegeten.'
    ]

    sents = list(doc.sents)
    assert [token.text for token in sents[0]] == ['=== Answer: 1234 ===\n']
    assert [token.text for token in sents[1]] == ['Dit', 'is', 'een', 'zin', '.', '\n']
    assert [token.text for token in sents[2]] == ['=== Report: 1234 ===\n']
    assert [token.text for token in sents[3]] == ['Mw.', 'heeft', 'goed', 'gegeten', '.']


def test_infix_split_on_parenthesis():
    text = 'GRZ(12-12-2020).'
    doc = tokenizer.parse_text(text)
    tokens = [t.text for t in doc]
    assert tokens == 'GRZ ( 12-12-2020 ) .'.split()


def test_infix_split_on_forward_slash():
    text = 'Groot/Kempers'
    doc = tokenizer.parse_text(text)
    tokens = [t.text for t in doc]
    assert tokens == 'Groot / Kempers'.split()


def test_infix_split_on_forward_slash_exclude_dates():
    text = '13/01/2020'
    doc = tokenizer.parse_text(text)
    tokens = [t.text for t in doc]
    assert tokens == ['13/01/2020']
