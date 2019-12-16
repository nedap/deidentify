from os.path import dirname, join

from deidentify.dataset.brat import load_brat_document
from deidentify.surrogates.dataset_deidentifier import (DatasetDeidentifier,
                                                        Document)


def _load_documents():
    doc_names = ['example-1', 'example-2']

    docs = []
    for doc in doc_names:
        annotations, text = load_brat_document(join(dirname(__file__), 'data/original'), doc)
        docs.append(Document(annotations, text))
    return docs


def test_dataset_deidentifier():
    docs = _load_documents()
    dataset_deidentifier = DatasetDeidentifier()
    docs = dataset_deidentifier.generate_surrogates(docs)

    print()
    for doc in docs:
        print('===================')
        for annotation, surrogate in zip(*doc.annotation_surrogate_pairs()):
            print('{:<30} => {:<20} ({})'.format(annotation.text, surrogate, annotation.tag))

            if annotation.tag == 'Other' or annotation.tag == 'Age':
                # other will be replaced manually, and there is no age above 89 in the test corpus
                assert annotation.text == surrogate
            else:
                assert annotation.text != surrogate
