from abc import ABC, abstractmethod
from typing import Iterable

import spacy
from loguru import logger


class Tokenizer(ABC):

    def __init__(self, disable: Iterable[str] = ()):
        """Tokenizer base class.

        Parameters
        ----------
        disable : Iterable[str]
            Steps of the spacy pipeline to disable.
            See: https://spacy.io/usage/processing-pipelines/#disabling

        """
        self.disable = disable

    @abstractmethod
    def parse_text(self, text: str) -> spacy.tokens.doc.Doc:
        pass


class TokenizerFactory():
    """Construct tokenizer instance per corpus. Currently, only the 'ons' corpus uses a custom
    spaCy tokenizer.

    For all other corpora, a wrapper around the default English spaCy tokenizer is used.
    """

    @staticmethod
    def tokenizer(corpus: str, disable: Iterable[str] = ()):
        logger.info('Tokenizer for corpus: {}'.format(corpus))
        if corpus.startswith('ons'):
            from deidentify.tokenizer.tokenizer_ons import TokenizerOns
            return TokenizerOns(disable=disable)

        from deidentify.tokenizer.tokenizer_en import TokenizerEN
        return TokenizerEN(disable=disable)
