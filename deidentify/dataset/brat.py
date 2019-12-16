from collections import defaultdict
from os.path import basename, join, splitext

from loguru import logger

from deidentify.base import Annotation


def load_brat_annotations(ann_file):
    """Load a brat standoff annotations (.ann) files.

    This method does not support brat fragment annotations. These annotations are inserted when
    annotating text spanning multiple lines.

    Example of fragment annotation that is not supported:
    `T30	Address 3232 3245;3246 3263	Calslaan 11 1234AB Wildervank`
    ```

    Parameters
    ----------
    ann_file : str
        Full path to .ann file.

    Returns
    -------
    list of deidentify.base.Annotation
        The annotations

    """
    annotations = []
    doc_id = splitext(basename(ann_file))[0]

    with open(ann_file) as file:
        lines = file.readlines()

    for line in lines:
        if not line.startswith('T'):
            continue

        splitted = line.split(None, 4)
        ann_id, tag, start, end, text = splitted
        text = text.rstrip('\n')
        try:
            annotation = Annotation(text=text, start=int(start), end=int(end), tag=tag,
                                    doc_id=doc_id, ann_id=ann_id)
            annotations.append(annotation)
        except ValueError:
            logger.warning(
                'Brat fragment annotations are not supported, skipping line\n{}'.format(line))

    return annotations


def load_brat_text(txt_file):
    # disable universal newline translation.
    # Otherwise there is a character mismatch between .ann/.txt files
    #
    # See https://github.com/nlplab/brat/issues/853
    with open(txt_file, newline='') as file:
        content = file.read()

    return content


def load_brat_document(path, doc_name):
    ann_file = join(path, '{}.ann'.format(doc_name))
    txt_file = join(path, '{}.txt'.format(doc_name))
    return load_brat_annotations(ann_file), load_brat_text(txt_file)


def write_brat_text(txt, output_file):
    # Disable universal newline translation.
    # Otherwise there is a character mismatch between .ann/.txt files
    #
    # See https://github.com/nlplab/brat/issues/853
    with open(output_file, 'w', newline='') as file:
        file.write(txt)


def write_brat_annotations(annotations, output_file):
    with open(output_file, 'w') as file:
        for annotation in annotations:
            annotation_txt = '{}\t{} {} {}\t{}\n'.format(annotation.ann_id,
                                                         annotation.tag,
                                                         annotation.start,
                                                         annotation.end,
                                                         annotation.text)

            file.write(annotation_txt)


def write_brat_document(path, doc_name, text, annotations):
    ann_file = join(path, '{}.ann'.format(doc_name))
    txt_file = join(path, '{}.txt'.format(doc_name))
    write_brat_annotations(annotations, ann_file)
    write_brat_text(text, txt_file)


def load_brat_config(config_file):
    with open(config_file) as f:
        sections = defaultdict(list)
        section = ''

        for line in f.readlines():
            line = line.strip()

            if not line or line.startswith('#') or line.startswith('!'):
                continue
            elif line.startswith('['):
                section = line[1:len(line) - 1]
            else:
                sections[section].append(line)

    return sections
