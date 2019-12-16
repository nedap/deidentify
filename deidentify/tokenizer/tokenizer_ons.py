"""
Custom tokenization routines for the 'ons' corpus. Special care is taken to metadata tokens such as
=== Report: 12345 === that were inserted to distinguish between multiple documents of a client.

They will be properly handled during the tokenization and sentence segmentation stage.
"""
import re

import spacy
from spacy.matcher import Matcher
from spacy.symbols import ORTH

from deidentify.tokenizer import Tokenizer

META_REGEX = re.compile(r'=== (?:Report|Answer): [0-9]+ ===\n')
TOKENIZER_SPECIAL_CASES = [
    'B.Sc.',
    'Co.',
    'Dhr.',
    'Dr.',
    'M.Sc.',
    'Mevr.',
    'Mgr.',
    'Mr.',
    'Mw.',
    'O.K.',
    'a.u.b.',
    'ca.',
    'e.g.',
    'etc.',
    'v.d.'
]


def _metadata_complete(doc, i):
    return doc[i].text[0] == '\n' \
        and doc[i - 1].text == '=' \
        and META_REGEX.match(doc[i - 9: i + 1].text)


def _metadata_sentence_segmentation(doc):
    """Custom sentence segmentation rule of the Ons corpus. It segments metadata text into separate
    sentences.

    Metadata consists of 10 tokens:
    ['=', '=', '=', 'Report|Answer', ':', 'DDDDDD', '=', '=', '=', '\n']

    During sentence segmentation, we want that the metadata is always a sentence in itself.
    Therefore, the first token (i.e., '=') is marked as sentence start. All other tokens
    are explicitly marked as non-sentence boundaries.

    To ensure that anything immediately following after metadata is a new sentece, the next token
    is marked as sentence start.
    """
    for i in range(len(doc)):
        if not _metadata_complete(doc, i):
            continue

        # All metadata tokens excluding the leading '='.
        meta_span = doc[i - 8: i + 1]
        for meta_token in meta_span:
            meta_token.is_sent_start = False
        # The leading '=' is a sentence boundary
        doc[i - 9].is_sent_start = True
        # Any token following the metadata is also a new sentence.
        doc[i + 1].is_sent_start = True
    return doc


NLP = spacy.load('nl_core_news_sm')
NLP.add_pipe(_metadata_sentence_segmentation, before="parser")  # Insert before the parser

for case in TOKENIZER_SPECIAL_CASES:
    NLP.tokenizer.add_special_case(case, [{ORTH: case}])
    NLP.tokenizer.add_special_case(case.lower(), [{ORTH: case.lower()}])


class TokenizerOns(Tokenizer):

    def parse_text(self, text: str) -> spacy.tokens.doc.Doc:
        """Custom spacy tokenizer for the 'ons' corpus that takes care of special metadata tokens.

        Example:
        ['=', '=', '=', 'Report', ':', '1234', '=', '=', '=', '\n'] is converted to
        ['=== Report: 1234 ===\n']

        Furthermore, common Dutch abbreviations are handled.

        Parameters
        ----------
        text : str
            The text to tokenize.

        Returns
        -------
        doc : spacy.tokens.doc.Doc
            Parsed spacy document.
        """
        matcher = Matcher(NLP.vocab)
        pattern = [
            {"ORTH": "="}, {"ORTH": "="}, {"ORTH": "="},
            {"ORTH": {"IN": ['Answer', 'Report']}}, {'ORTH': ':'},
            {'IS_DIGIT': True, 'OP': '+'},
            {"ORTH": "="}, {"ORTH": "="}, {"ORTH": "="},
            {"ORTH": "\n"}
        ]
        matcher.add("METADATA", None, pattern)

        doc = NLP(text, disable=self.disable)
        matches = matcher(doc)

        with doc.retokenize() as retokenizer:
            for _, start, end in matches:
                attrs = {"LEMMA": str(doc[start:end])}
                retokenizer.merge(doc[start:end], attrs=attrs)

        return doc
