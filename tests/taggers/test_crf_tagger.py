from deidentify.base import Annotation, Document
from deidentify.taggers import CRFTagger
from deidentify.tokenizer import TokenizerFactory

tokenizer = TokenizerFactory().tokenizer(corpus='ons')
tagger = CRFTagger(model='model_crf_ons_tuned-v0.1.0', tokenizer=tokenizer)


def test_annotate():
    doc = Document(
        name='',
        text='Hij werd op 10 oktober door arts Peter de Visser ontslagen van de kliniek.', annotations=[]
    )

    anns = tagger.annotate([doc])[0].annotations
    assert anns == [
        Annotation(text='10 oktober', start=12, end=22, tag='Date', doc_id='', ann_id='T0'),
        Annotation(text='Peter de Visser', start=33, end=48, tag='Name', doc_id='', ann_id='T1')
    ]


def test_tags():
    expected = [
        'SSN',
        'Organization_Company',
        'Date',
        'ID',
        'Internal_Location',
        'Care_Institute',
        'Age',
        'Phone_fax',
        'Name',
        'Profession',
        'Hospital',
        'Other',
        'Initials',
        'Address',
        'Email',
        'URL_IP'
    ]
    assert sorted(tagger.tags) == sorted(expected)
