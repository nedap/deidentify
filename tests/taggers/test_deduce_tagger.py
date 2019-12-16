from deidentify.base import Annotation, Document
from deidentify.taggers import DeduceTagger


def test_annotate():
    tagger = DeduceTagger()
    doc = Document(name='', text='Jan Jannsen vanuit het UMCU.', annotations=[])
    anns = tagger.annotate([doc])[0].annotations

    assert anns == [
        Annotation(text='Jan Jannsen', start=0, end=11, tag='Name', doc_id='', ann_id='T0'),
        Annotation(text='UMCU', start=23, end=27, tag='Named_Location', doc_id='', ann_id='T1')
    ]


def test_tags():
    tagger = DeduceTagger()

    assert sorted(tagger.tags) == sorted(
        ['ID', 'URL_IP', 'Date', 'Phone_fax', 'Address', 'Name', 'Age', 'Named_Location'])
