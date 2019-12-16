import spacy

from deidentify.tokenizer import Tokenizer

NLP = spacy.load('en_core_web_sm')


class TokenizerEN(Tokenizer):

    def parse_text(self, text: str) -> spacy.tokens.doc.Doc:
        return NLP(text)
