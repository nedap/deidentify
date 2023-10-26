from pathlib import Path

from deidentify.base import Corpus, Document
from deidentify.dataset import brat

BASE_PATH = Path(__file__).resolve().parent / '../../data/corpus'
DUMMY_CORPUS = BASE_PATH / 'dummy'
CORPUS_PATH = {p.name: p for p in BASE_PATH.glob('*/')}


class CorpusLoader:

    @staticmethod
    def _load_folder(path: Path):
        files = path.glob('*.ann')
        files = sorted(files)

        documents = []
        for file in files:
            doc_name = file.stem
            annotations, text = brat.load_brat_document(path, doc_name)
            doc = Document(name=doc_name, text=text, annotations=annotations)
            documents.append(doc)

        return documents

    def load_corpus(self, path) -> Corpus:
        path = Path(path)
        corpus_name = path.name

        train = self._load_folder(path / 'train')
        test = self._load_folder(path / 'test')
        dev = self._load_folder(path / 'dev')

        return Corpus(train=train, test=test, dev=dev, name=corpus_name)
