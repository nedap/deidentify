import argparse
import glob
import os
import shutil
from os.path import basename, join, splitext

import pandas as pd
from loguru import logger

from deidentify.base import Annotation
from deidentify.dataset.brat import load_brat_text, write_brat_document


def apply_surrogates(text, annotations, surrogates):
    adjusted_annotations = []
    # Amount of characters by which start point of annotation is adjusted
    # Positive shift if surrogates are longer than original annotations
    # Negative shift if surrogates are shorter
    shift = 0

    original_text_pointer = 0
    text_rewritten = ''

    for annotation, surrogate in zip(annotations, surrogates):
        part = text[original_text_pointer:annotation.start]

        start = annotation.start + shift
        end = start + len(surrogate)
        shift += len(surrogate) - len(annotation.text)

        adjusted_annotations.append(Annotation(
            text=surrogate,
            start=start,
            end=end,
            tag=annotation.tag,
            doc_id=annotation.doc_id,
            ann_id=annotation.ann_id
        ))

        text_rewritten += part + surrogate
        original_text_pointer = annotation.end

    text_rewritten += text[original_text_pointer:]
    return text_rewritten, adjusted_annotations


def main(args):
    df_surrogates = pd.read_csv(args.surrogate_table)
    logger.info('Rewrite {} files.'.format(len(df_surrogates.doc_id.unique())))

    # Use manual surrogate if it exists. If not, use the automatically generated one
    df_surrogates['surrogate'] = df_surrogates.manual_surrogate.fillna(df_surrogates['surrogate'])

    for doc_id, rows in df_surrogates.groupby('doc_id'):
        text = load_brat_text(join(args.data_path, '{}.txt'.format(doc_id)))

        rows = rows.sort_values(by='start')
        annotations = rows.apply(lambda row: Annotation(
            text=row['text'],
            start=row['start'],
            end=row['end'],
            tag=row['tag'],
            doc_id=row['doc_id'],
            ann_id=row['ann_id']
        ), axis=1)

        surrogates = rows.surrogate.values

        text_rewritten, adjusted_annotations = apply_surrogates(text, annotations, surrogates)

        write_brat_document(args.output_path, doc_id,
                            text=text_rewritten, annotations=adjusted_annotations)

    files_with_annotations = set(df_surrogates.doc_id.values)
    all_files = [splitext(basename(f))[0] for f in glob.glob(join(args.data_path, '*.txt'))]
    files_without_annotations = [f for f in all_files if f not in files_with_annotations]
    logger.info('Found {} files without any annotations. '
                'Copy them to output_path...'.format(len(files_without_annotations)))

    for file in files_without_annotations:
        shutil.copy2(join(args.data_path, '{}.txt'.format(file)), args.output_path)
        shutil.copy2(join(args.data_path, '{}.ann'.format(file)), args.output_path)

    logger.info('Done.')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("surrogate_table",
                        help="Annotation to surrogate mapping table (CSV format).")
    parser.add_argument("data_path", help="Full path original Brat text files.")
    parser.add_argument("output_path", help="Directory to write replaced .txt/.ann files to.")
    return parser.parse_args()


if __name__ == '__main__':
    args = arg_parser()
    os.makedirs(args.output_path, exist_ok=True)
    main(args)
