import argparse
import csv
import glob
import os
import sys
from os.path import basename, dirname, exists, join, splitext

from loguru import logger

from deidentify.dataset.brat import load_brat_document
from deidentify.surrogates.dataset_deidentifier import (DatasetDeidentifier,
                                                        Document)


def _load_docs(dataset_path):
    ann_files = sorted(glob.glob(join(dataset_path, '*.ann')))

    docs = []
    for ann_file in ann_files:
        doc_name = splitext(basename(ann_file))[0]
        annotations, text = load_brat_document(dataset_path, doc_name)
        docs.append(Document(annotations=annotations, text=text))

    return docs


def main(args):
    docs = _load_docs(args.dataset_path)
    logger.info('Found {} documents.', len(docs))

    logger.info('Start surrogate generation...')
    dataset_deidentifier = DatasetDeidentifier()
    docs = dataset_deidentifier.generate_surrogates(docs)

    logger.info('Export results...')
    with open(args.output_file, mode='w') as result_file:
        csv_writer = csv.writer(result_file,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)

        csv_writer.writerow(['doc_id', 'ann_id', 'text', 'start', 'end', 'tag', 'surrogate',
                             'manual_surrogate', 'checked'])

        for doc in docs:
            annotations, surrogates = doc.annotation_surrogate_pairs()

            for annotation, surrogate in zip(annotations, surrogates):
                csv_writer.writerow([
                    annotation.doc_id,
                    annotation.ann_id,
                    annotation.text,
                    annotation.start,
                    annotation.end,
                    annotation.tag,
                    surrogate,
                    '',
                    False
                ])

    logger.info('Done.')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_path", help="Path to brat dataset.")
    parser.add_argument("output_file", help="Full path to output CSV file.")
    return parser.parse_args()


if __name__ == '__main__':
    args = arg_parser()
    log_filename = 'surrogate-generation.log'

    logger.remove(0)
    logger.add(sys.stderr, level="INFO")

    logger.add(join(dirname(__file__), '../../logs/', log_filename))
    logger.info('Surrogate generator configuration: {}', args)

    if exists(args.output_file):
        logger.info('Output file already exists, please choose another name.')
        exit(0)
    os.makedirs(dirname(args.output_file), exist_ok=True)

    main(args)
