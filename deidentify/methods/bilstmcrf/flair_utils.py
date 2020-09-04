"""Utility module to convert between the standoff document representation used in this project and
the flair Corpus format. Methods operate on the sentence level and integrate with `deidentify.methods.tagging_utils`.
"""
import sys
from functools import reduce
from typing import List, Tuple

from flair.data import Corpus, Sentence, Token
from torch.nn.modules.module import _addindent

from deidentify.base import Document
from deidentify.methods.tagging_utils import ParsedDoc, sents_to_standoff, standoff_to_sents
from deidentify.tokenizer import Tokenizer


class FilteredCorpus(Corpus):

    def __init__(self, train: List[Sentence], dev: List[Sentence], test: List[Sentence],
                 ignore_sentence, name: str = "corpus"):
        self.ignore_sentence = ignore_sentence

        train, self.train_ignored = self._filter_sentences(train)
        dev, self.dev_ignored = self._filter_sentences(dev)
        test, self.test_ignored = self._filter_sentences(test)

        super(FilteredCorpus, self).__init__(
            train=train,
            dev=dev,
            test=test,
            name=name
        )

    def _filter_sentences(self, sents: List[Sentence]):
        include, ignore = [], []
        for sent in sents:
            if self.ignore_sentence(sent):
                ignore.append(sent)
            else:
                include.append(sent)
        return include, ignore

    def __str__(self):
        t = u"FilteredCorpus(): train = {}, dev = {}, test = {}. Ignored train/dev/test = {}/{}/{}"
        return t.format(len(self._train), len(self.dev), len(self._test),
                        len(self.train_ignored), len(self.dev_ignored), len(self.test_ignored))

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


def standoff_to_flair_sents(docs: List[Document],
                            tokenizer: Tokenizer,
                            verbose=False) -> Tuple[List[Sentence], List[ParsedDoc]]:
    sents, parsed_docs = standoff_to_sents(docs=docs, tokenizer=tokenizer, verbose=verbose)

    flair_sents = []
    for sent in sents:
        flair_sent = Sentence()
        for token in sent:
            if token.text.isspace():
                # spaCy preserves consecutive whitespaces, while flair ignores them.
                # This would make a round-trip standoff -> token -> standoff impossible.
                # To accommodate whitespace tokens with flair, we add a special token.
                tok = Token('<SPACE>')
            else:
                tok = Token(token.text)
            tok.add_tag(tag_type='ner', tag_value=token.label)
            flair_sent.add_token(tok)
        flair_sents.append(flair_sent)

    return flair_sents, parsed_docs


def flair_sents_to_standoff(tagged_flair_sentences: List[Sentence],
                            docs: List[ParsedDoc]) -> List[Document]:

    sentence_tags = []
    for sent in tagged_flair_sentences:
        sentence_tags.append([token.get_tag('ner').value for token in sent])

    return sents_to_standoff(sentence_tags, docs)


def model_summary(model, file=sys.stderr):
    def tree_repr(model):
        # We treat the extra repr like the sub-module, one item per line
        extra_lines = []
        extra_repr = model.extra_repr()
        # empty string will be split into list ['']
        if extra_repr:
            extra_lines = extra_repr.split('\n')
        child_lines = []
        total_params = 0
        for key, module in model._modules.items():
            mod_str, num_params = tree_repr(module)
            mod_str = _addindent(mod_str, 2)
            child_lines.append('(' + key + '): ' + mod_str)
            total_params += num_params
        lines = extra_lines + child_lines

        for name, p in model._parameters.items():
            total_params += reduce(lambda x, y: x * y, p.shape)

        main_str = model._get_name() + '('
        if lines:
            # simple one-liner info, which most builtin Modules will use
            if len(extra_lines) == 1 and not child_lines:
                main_str += extra_lines[0]
            else:
                main_str += '\n  ' + '\n  '.join(lines) + '\n'

        main_str += ')'
        if file is sys.stderr:
            main_str += ', \033[92m{:,}\033[0m params'.format(total_params)
        else:
            main_str += ', {:,} params'.format(total_params)
        return main_str, total_params

    string, count = tree_repr(model)
    if file is not None:
        print(string, file=file)
    return count
