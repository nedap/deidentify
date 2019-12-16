from flair.data import Sentence

from deidentify.dataset.corpus_loader import DUMMY_CORPUS, CorpusLoader
from deidentify.methods.bilstmcrf import flair_utils
from deidentify.tokenizer import TokenizerFactory


def test_standoff_to_flair_sents():
    corpus = CorpusLoader().load_corpus(DUMMY_CORPUS)
    tokenizer = TokenizerFactory().tokenizer('ons')
    docs = corpus.train
    sents, parsed_docs = flair_utils.standoff_to_flair_sents(docs, tokenizer)

    assert len(sents) == 10
    assert len(parsed_docs) == 10

    bio_tags = [token.get_tag('ner').value for token in sents[0]]
    token_texts = [token.text for token in sents[0]]

    assert token_texts == [
        'Linders',
        ',',
        'Xandro',
        '<',
        't.njg.nmmeso@rcrmb.nl',
        '>',
        '\n',
        '07',
        'apr',
        '.',
        '\n\n',
    ]

    assert bio_tags == [
        'B-Name',
        'I-Name',
        'I-Name',
        'O',
        'B-Email',
        'O',
        'O',
        'B-Date',
        'I-Date',
        'O',
        'O',
    ]


def test_flair_sents_to_standoff():
    corpus = CorpusLoader().load_corpus(DUMMY_CORPUS)
    tokenizer = TokenizerFactory().tokenizer('ons')
    docs_expected = corpus.train

    sents, parsed_docs = flair_utils.standoff_to_flair_sents(docs_expected, tokenizer)
    docs_actual = flair_utils.flair_sents_to_standoff(sents, parsed_docs)

    assert len(docs_actual) == 1
    assert len(docs_expected) == 1

    assert len(docs_actual[0].annotations) == 16
    assert len(docs_expected[0].annotations) == 16

    for ann_expected, ann_actual in zip(docs_expected[0].annotations, docs_actual[0].annotations):
        assert ann_expected.text == ann_actual.text
        assert ann_expected.tag == ann_actual.tag


def test_filtered_corpus():
    def ignore_sentence(sent):
        return sent[0].text.startswith('===')

    filtered_corpus = flair_utils.FilteredCorpus(
        train=[Sentence('=== Answer: 123 ==='), Sentence('this is should be included')],
        dev=[Sentence('this is should be included'), Sentence('=== Answer: 456 ===')],
        test=[Sentence('this is should be included'), Sentence('and this as well')],
        ignore_sentence=ignore_sentence
    )

    assert len(filtered_corpus.train) == 1
    assert filtered_corpus.train[0].to_plain_string() == 'this is should be included'
    assert len(filtered_corpus.dev) == 1
    assert filtered_corpus.dev[0].to_plain_string() == 'this is should be included'
    assert len(filtered_corpus.test) == 2
    assert filtered_corpus.test[0].to_plain_string() == 'this is should be included'
    assert filtered_corpus.test[1].to_plain_string() == 'and this as well'

    assert len(filtered_corpus.train_ignored) == 1
    assert filtered_corpus.train_ignored[0].to_plain_string() == '=== Answer: 123 ==='
    assert len(filtered_corpus.dev_ignored) == 1
    assert filtered_corpus.dev_ignored[0].to_plain_string() == '=== Answer: 456 ==='
    assert len(filtered_corpus.test_ignored) == 0



if __name__ == '__main__':
    corpus = CorpusLoader().load_corpus(DUMMY_CORPUS)
    tokenizer = TokenizerFactory().tokenizer('ons')
    docs = corpus.train
    sents, parsed_docs = flair_utils.standoff_to_flair_sents(docs, tokenizer)

    print(repr(docs[0].text))
    for sent in sents:
        print(' '.join([repr(token.text) for token in sent.tokens]))
