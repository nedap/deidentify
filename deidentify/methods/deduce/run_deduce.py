import argparse
import re
from typing import List

import deduce
from loguru import logger
from tqdm import tqdm

from deidentify.methods import train_utils
from deidentify.base import Document
from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.methods.deduce.deduce_labeler import DeduceAnnotator

NAME_PREFIX_REGEX = re.compile(r'({})\.?\s*'.format('|'.join(deduce.lookup_lists.PREFIXES)),
                               re.IGNORECASE)

DEDUCE_ONS_TAG_MAPPING = {
    "PATIENT": 'Name',
    "PERSOON": 'Name',
    "LOCATIE":  'Address',
    "INSTELLING": 'Named_Location',
    "DATUM": 'Date',
    "LEEFTIJD": 'Age',
    "PATIENTNUMMER": 'ID',
    "TELEFOONNUMMER": 'Phone_fax',
    "URL": 'URL_IP',
}


def apply_tag_mapping(annotation):
    return annotation._replace(tag=DEDUCE_ONS_TAG_MAPPING[annotation.tag])


def rewrite_annotations(text, annotations):
    rewritten = []

    for annotation in annotations:
        annotation = apply_tag_mapping(annotation)

        if annotation.tag == 'ID' and text[annotation.end:annotation.end + 4] == ' ===':
            # In the 'ons' corpus, metadata is present in form of === Answer: {ID} ===
            # If deduce mistakenly annotated a metadata ID, we drop this annotation
            continue
        elif annotation.tag == 'Name':
            if NAME_PREFIX_REGEX.match(annotation.text):
                # Prefixes are not considered PHI in the 'ons' corpus, so they are dropped from
                # the Deduce annotations.
                substituted = NAME_PREFIX_REGEX.sub('', annotation.text)

                if not substituted.strip():
                    # Annotation only consists of name prefix. We drop such annotations.
                    continue

                chars_removed = len(annotation.text) - len(substituted)
                new_start = annotation.start + chars_removed

                annotation = annotation._replace(text=substituted, start=new_start)

        rewritten.append(annotation)
    return rewritten


def predict(documents: List[Document], corpus_name='ons', verbose=False) -> List[Document]:
    predictions = []

    for doc in tqdm(documents, disable=not verbose, desc='Tag documents'):
        annotator = DeduceAnnotator(doc.text)
        annotations = annotator.annotations()
        if corpus_name.startswith('ons'):
            annotations = rewrite_annotations(doc.text, annotations)

        new_doc = Document(name=doc.name, text=doc.text, annotations=annotations)
        predictions.append(new_doc)

    return predictions


def main(args):
    corpus = CorpusLoader().load_corpus(CORPUS_PATH[args.corpus])
    logger.info('Loaded corpus: {}'.format(corpus))
    logger.info('Make predictions...')
    train_utils.save_predictions(corpus_name=corpus.name, run_id='deduce_' + args.run_id,
                                train=predict(corpus.train, corpus_name=corpus.name, verbose=True),
                                dev=predict(corpus.dev, corpus_name=corpus.name, verbose=True),
                                test=predict(corpus.test, corpus_name=corpus.name, verbose=True))
    logger.info('Done.')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", choices=CORPUS_PATH.keys(), help="Corpus identifier.")
    parser.add_argument("run_id", help="Run Identifier")
    return parser.parse_args()


if __name__ == '__main__':
    main(arg_parser())
