import argparse
import glob
from os.path import basename, isdir, join, splitext
from typing import List

from deidentify.base import Document
from deidentify.dataset import brat
from deidentify.evaluation.evaluator import Evaluator


def _basenames(files):
    return list(map(lambda f: splitext(basename(f))[0], files))


def get_documents(docs_path, anns_path) -> List[Document]:
    if not isdir(docs_path):
        raise ValueError('docs_path = {} does not exist.'.format(docs_path))
    if not isdir(anns_path):
        raise ValueError('anns_path = {} does not exist.'.format(anns_path))

    txt_files = sorted(glob.glob(join(docs_path, '*.txt')))
    ann_files = sorted(glob.glob(join(anns_path, '*.ann')))

    assert ann_files and txt_files and _basenames(txt_files) == _basenames(ann_files)

    docs = []
    for txt_file, ann_file in zip(txt_files, ann_files):
        doc_name = splitext(basename(txt_file))[0]
        doc_txt = brat.load_brat_text(txt_file)
        doc_annos = brat.load_brat_annotations(ann_file)

        docs.append(Document(name=doc_name, text=doc_txt, annotations=doc_annos))

    return docs


def evaluate_documents(gold_docs, pred_docs, language='nl'):
    return Evaluator(gold_docs, pred_docs, language=language)


def evaluate(documents_path, gold_path, pred_path, language='nl'):
    gold_docs = get_documents(documents_path, gold_path)
    pred_docs = get_documents(documents_path, pred_path)
    return evaluate_documents(gold_docs, pred_docs, language=language)


def main(args):
    evaluator = evaluate(args.documents_path, args.gold_path, args.pred_path, args.language)

    print()
    print(evaluator.entity_level())
    print()
    print(evaluator.token_level())
    print()
    print(evaluator.token_level_blind())


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("language", help="Language to use for tokenizer",
                        choices=Evaluator.supported_languages())
    parser.add_argument("documents_path", help="Path to *.txt files")
    parser.add_argument("gold_path", help="Path to gold *.ann files")
    parser.add_argument("pred_path", help="Path to predicted *.ann files")
    return parser.parse_args()


if __name__ == '__main__':
    main(arg_parser())
