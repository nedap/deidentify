from typing import List

from flair.models import SequenceTagger
from loguru import logger

from deidentify.base import Document
from deidentify.methods.bilstmcrf import flair_utils
from deidentify.taggers.base import TextTagger, lookup_model
from deidentify.tokenizer import Tokenizer


class FlairTagger(TextTagger):

    def __init__(self, model, tokenizer: Tokenizer, mini_batch_size=256, verbose=False):
        self.tokenizer = tokenizer
        self.mini_batch_size = mini_batch_size
        self.verbose = verbose

        model_file = lookup_model(model)
        logger.info('Load flair model from {}'.format(model_file))
        self.tagger = SequenceTagger.load(model_file)
        logger.info('Finish loading flair model.')

    def annotate(self, documents: List[Document]) -> List[Document]:
        flair_sents, parsed_docs = flair_utils.standoff_to_flair_sents(
            docs=documents,
            tokenizer=self.tokenizer,
            verbose=self.verbose
        )

        self.tagger.predict(flair_sents, mini_batch_size=self.mini_batch_size, verbose=self.verbose)

        annotated_docs = flair_utils.flair_sents_to_standoff(flair_sents, parsed_docs)
        return annotated_docs

    @property
    def tags(self):
        bio_tag_names = self.tagger.tag_dictionary.get_items()
        bio_tag_names.remove('<unk>')
        bio_tag_names.remove('<START>')
        bio_tag_names.remove('<STOP>')

        tags = set()
        for bio_tag in bio_tag_names:
            if bio_tag == 'O':
                tags.add('O')
            else:
                name = bio_tag.split('-', maxsplit=1)[1]
                tags.add(name)
        return list(tags)
