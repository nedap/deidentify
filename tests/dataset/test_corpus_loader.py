from deidentify.dataset import corpus_loader


def test_corpus_loader_dummy_corpus():
    loader = corpus_loader.CorpusLoader()
    corpus = loader.load_corpus(corpus_loader.DUMMY_CORPUS)

    assert len(corpus.train) == 1
    assert len(corpus.test) == 1
    assert len(corpus.dev) == 1

    assert len(corpus.train[0].text) >= 500
    assert len(corpus.train[0].annotations) == 16
