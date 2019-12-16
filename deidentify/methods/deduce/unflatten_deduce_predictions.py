"""Restores original (unflattened) tag from flattened DEDUCE output.

DEDUCE does not distinguish between hospitals, companies, care institutes and other named locations.
Therefore, we both mapped the gold standard corpus as well as the DEDUCE output to a more generic
tagset (see `FLAT_TAG_MAPPING` below and `deidentify/methods/deduce/flatten_ons_corpus.sh`).

For the significance testing, we need to make the two tagging schemes comparable again, otherwise
the scores are pessimistic.

This script re-maps the flattened DEDUCE tags to their original counter-part based on the original
train/dev/test instances. This is only done if **entity boundaries match exactly**.

Note: this cannot be done in practice, as one does not know the ground truth label. So this is only
a post-processing step in the evaluation process.
"""
import argparse
from os.path import dirname, join

from deidentify.methods import train_utils
from deidentify.base import Document
from deidentify.evaluation import evaluate_run

FLAT_TAG_MAPPING = {
    "Hospital": "Named_Location",
    "Care_Institute": "Named_Location",
    "Organization_Company": "Named_Location",
    "Internal_Location": "Named_Location",
    "Email": "URL_IP",
}


def _gold_path(corpus, part):
    return join(dirname(__file__), '../../../data/corpus', corpus, part)


def _predictions_path(corpus, run_id, part):
    return join(dirname(__file__), '../../../output/predictions', corpus, run_id, part)


def _flat_to_gold_mapping(gold_docs):
    tag_mapping = {}

    for doc in gold_docs:
        for ann in doc.annotations:
            try:
                flat_tag = FLAT_TAG_MAPPING[ann.tag]
                tag_mapping[(doc.name, ann.start, ann.end, flat_tag)] = ann.tag
            except KeyError:
                continue

    return tag_mapping


def _unflatten_tags(tag_mapping, documents):
    replaced_docs = []

    for doc in documents:
        new_annotations = []
        for ann in doc.annotations:
            ann_key = (doc.name, ann.start, ann.end, ann.tag)
            new_tag = tag_mapping.get(ann_key, ann.tag)
            new_ann = ann._replace(tag=new_tag)
            new_annotations.append(new_ann)
        replaced_docs.append(Document(name=doc.name, text=doc.text, annotations=new_annotations))

    return replaced_docs


def _map_annotations(args, part):
    gold_path = _gold_path(args.corpus, part)
    gold_docs = evaluate_run.get_documents(gold_path, gold_path)

    flat_corpus_name = '{}-flattened'.format(args.corpus)
    flat_corpus_path = _gold_path(flat_corpus_name, part)
    flat_predictions_path = _predictions_path(flat_corpus_name, args.run_id, part)
    predicted_docs = evaluate_run.get_documents(flat_corpus_path, flat_predictions_path)

    tag_mapping = _flat_to_gold_mapping(gold_docs)
    return _unflatten_tags(tag_mapping, predicted_docs)


def main(args):
    train_utils.save_predictions(corpus_name='ons', run_id='{}_unflattened'.format(args.run_id),
                                train=_map_annotations(args, 'train'))
    train_utils.save_predictions(corpus_name='ons', run_id='{}_unflattened'.format(args.run_id),
                                dev=_map_annotations(args, 'dev'))
    train_utils.save_predictions(corpus_name='ons', run_id='{}_unflattened'.format(args.run_id),
                                test=_map_annotations(args, 'test'))


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", help="Corpus identifier.")
    parser.add_argument("run_id", help="Run identifier")
    return parser.parse_args()


if __name__ == '__main__':
    main(arg_parser())
