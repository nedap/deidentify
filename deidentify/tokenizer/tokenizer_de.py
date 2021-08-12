import spacy

from deidentify.tokenizer import Tokenizer

NLP = spacy.load('de_core_news_sm')


class TokenizerDE(Tokenizer):

    def parse_text(self, text: str) -> spacy.tokens.doc.Doc:
        return NLP(text)
