import glob
from os.path import basename, dirname, join, normpath, splitext

from deidentify.base import Corpus, Document
from deidentify.dataset import brat

BASE_PATH = join(dirname(__file__), '../../data/corpus/')
DUMMY_CORPUS = join(BASE_PATH, 'dummy/')

_CORPUS_DIRS = map(lambda dir: basename(normpath(dir)), glob.glob(BASE_PATH + '/*/'))
CORPUS_PATH = {c: join(BASE_PATH, c + '/') for c in _CORPUS_DIRS}


def get_basename(full_path):
    return splitext(basename(full_path))[0]


class CorpusLoader:

    @staticmethod
    def _load_folder(path):
        files = glob.glob(join(path, '*.ann'))
        files = sorted(files)

        documents = []
        for file in files:
            doc_name = get_basename(file)
            annotations, text = brat.load_brat_document(path, doc_name)
            doc = Document(name=doc_name, text=text, annotations=annotations)
            documents.append(doc)

        return documents

    def load_corpus(self, path) -> Corpus:
        corpus_name = basename(normpath(path))

        train = self._load_folder(join(path, 'train'))
        test = self._load_folder(join(path, 'test'))
        dev = self._load_folder(join(path, 'dev'))

        return Corpus(train=train, test=test, dev=dev, name=corpus_name)
