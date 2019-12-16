import argparse
import os
import re
from typing import Dict, List

from deidentify.base import Annotation, Document
from deidentify.dataset import brat


def readlines(filename):
    with open(filename) as file:
        lines = file.readlines()
    return lines


def documents_iter(notes):
    lines = readlines(notes)

    record_lines = []
    for line in lines:
        if line.startswith('START_OF_RECORD'):
            record_lines = []
            patient_id, record_id = re.findall(r'\d+', line)
        elif line.startswith('||||END_OF_RECORD'):
            yield Document(
                name='note-{}-{}'.format(patient_id, record_id),
                text=''.join(record_lines).rstrip(),
                annotations=[]
            )
        else:
            record_lines.append(line)


def annotations_iter(annotations):
    lines = readlines(annotations)

    current_pid, current_rid = lines[0].split(maxsplit=5)[0:2]

    annotations = []
    i = 1
    for line in lines:
        pid, rid, start, end, tag, text = line.strip().split(maxsplit=5)
        if pid != current_pid or rid != current_rid:
            yield annotations
            annotations = []
            i = 1
            current_pid = pid
            current_rid = rid

        annotations.append(Annotation(
            text=text,
            start=int(start),
            end=int(end),
            tag=tag,
            ann_id='T{}'.format(i),
            doc_id='note-{}-{}'.format(current_pid, current_rid)
        ))
        i += 1

    yield annotations


def _map_annotations(annotations):
    # Mapping: doc_id -> List[Annotation]
    mapping: Dict[str, List[Annotation]] = {}

    for doc_anns in annotations:
        mapping[doc_anns[0].doc_id] = doc_anns

    return mapping


def main(args):
    documents = documents_iter(args.notes_file)
    annotations = annotations_iter(args.phi_file)

    doc_annotations_mapping = _map_annotations(annotations)

    for doc in documents:
        anns = doc_annotations_mapping.get(doc.name, [])
        brat.write_brat_document(args.output_dir, doc_name=doc.name,
                                 text=doc.text, annotations=anns)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("notes_file", help="Full path to raw notes file (notes-raw.txt)")
    parser.add_argument("phi_file", help="Full path to annotations file (id-phi.phrase)")
    parser.add_argument("output_dir", help="Path to output directory.")
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()
    os.makedirs(ARGS.output_dir, exist_ok=True)
    main(ARGS)
