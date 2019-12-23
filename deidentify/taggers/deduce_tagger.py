from typing import List

from deidentify.base import Document
from deidentify.methods.deduce import run_deduce
from deidentify.taggers.base import TextTagger


class DeduceTagger(TextTagger):

    def __init__(self, verbose=False):
        self.verbose = verbose

    def annotate(self, documents: List[Document]) -> List[Document]:
        docs_predicted = run_deduce.predict(documents, verbose=self.verbose)
        return docs_predicted

    @property
    def tags(self):
        return list(set(run_deduce.DEDUCE_ONS_TAG_MAPPING.values()))
