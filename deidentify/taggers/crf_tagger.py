import pickle
from typing import List

from loguru import logger

from deidentify.base import Document
from deidentify.methods import tagging_utils
from deidentify.methods.crf import crf_labeler, crf_util
from deidentify.taggers.base import TextTagger, lookup_model
from deidentify.tokenizer import Tokenizer


class CRFTagger(TextTagger):

    def __init__(self, model, tokenizer: Tokenizer, verbose=False):
        self.tokenizer = tokenizer
        self.feature_extractor, self.meta_sentence_filter = crf_util.FEATURE_EXTRACTOR['liu_2015']
        self.verbose = verbose

        model_file = lookup_model(model)
        logger.info('Load sklearn-crfsuite model from {}'.format(model_file))
        with open(model_file, 'rb') as clf_file:
            self.tagger = pickle.load(clf_file)
        logger.info('Finish loading crf model.')

    def annotate(self, documents: List[Document]) -> List[Document]:
        sents, parsed_docs = tagging_utils.standoff_to_sents(
            docs=documents,
            tokenizer=self.tokenizer,
            verbose=self.verbose
        )

        X_features, _ = crf_labeler.sents_to_features_and_labels(sents, self.feature_extractor)
        y_pred = self.tagger.predict(X_features, verbose=self.verbose)
        annotated_docs = tagging_utils.sents_to_standoff(y_pred, parsed_docs)
        return annotated_docs

    @property
    def tags(self):
        bio_tag_names = self.tagger.classes_
        bio_tag_names.remove('O')

        targets = set()
        for target in bio_tag_names:
            if target == 'O':
                targets.add('O')
            else:
                name = target.split('-', maxsplit=1)[1]
                targets.add(name)

        return list(targets)
