from os.path import dirname, join

from deidentify.base import Annotation
from deidentify.dataset.brat import load_brat_document
from deidentify.surrogates.dataset_deidentifier import DatasetDeidentifier, Document


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


def test_generate_surrogates_without_choices():
    text = 'Patient is being treated at UMCU.'
    annotations = [Annotation('UMCU', text.index('UMCU'), text.index('UMCU') + 4, 'Hospital')]
    doc = Document(annotations, text)

    surrogate_doc = DatasetDeidentifier().generate_surrogates([doc])[0]

    original_annotations, surrogates = surrogate_doc.annotation_surrogate_pairs()
    assert len(original_annotations) == 1
    assert len(surrogates) == 1
    assert original_annotations[0].text == 'UMCU'
    assert surrogates[0] == 'UMCU'


def test_generate_surrogates_shuffle_choices():
    text = 'Patient is being treated at UMCU.'
    annotations = [Annotation('UMCU', text.index('UMCU'), text.index('UMCU') + 4, 'Hospital')]
    doc_1 = Document(annotations, text)

    text = 'Patient is being treated at MST.'
    annotations = [Annotation('MST', text.index('MST'), text.index('MST') + 3, 'Hospital')]
    doc_2 = Document(annotations, text)

    surrogate_docs = DatasetDeidentifier().generate_surrogates([doc_1, doc_2])

    original_annotations, surrogates = surrogate_docs[0].annotation_surrogate_pairs()
    assert len(original_annotations) == 1 and len(surrogates) == 1
    assert original_annotations[0].text == 'UMCU'
    assert surrogates[0] == 'MST'

    original_annotations, surrogates = surrogate_docs[1].annotation_surrogate_pairs()
    assert len(original_annotations) == 1 and len(surrogates) == 1
    assert original_annotations[0].text == 'MST'
    assert surrogates[0] == 'UMCU'
