import spacy

from deidentify.tokenizer import Tokenizer

NLP = spacy.load('fr_core_news_sm')


class TokenizerFR(Tokenizer):

    def parse_text(self, text: str) -> spacy.tokens.doc.Doc:
        return NLP(text)
