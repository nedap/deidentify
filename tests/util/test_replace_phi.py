import re

import pytest

from deidentify.base import Annotation, Document
from deidentify.util import mask_annotations, surrogate_annotations


def test_mask_annotations():
    text = "De patient J. Jansen (e: j.jnsen@email.com, t: 06-12345678)"
    annotations = [
        Annotation(text='J. Jansen', start=11, end=20, tag='Name', doc_id='', ann_id='T0'),
        Annotation(text='j.jnsen@email.com', start=25, end=42, tag='Email', doc_id='', ann_id='T1'),
        Annotation(text='06-12345678', start=47, end=58, tag='Phone_fax', doc_id='', ann_id='T2')
    ]

    doc = Document(name='test_doc', text=text, annotations=annotations)

    doc = mask_annotations(doc)
    assert doc.text == "De patient [NAME] (e: [EMAIL], t: [PHONE_FAX])"
    assert doc.annotations == [
        Annotation(text='[NAME]', start=11, end=17, tag='Name', doc_id='', ann_id='T0'),
        Annotation(text='[EMAIL]', start=22, end=29, tag='Email', doc_id='', ann_id='T1'),
        Annotation(text='[PHONE_FAX]', start=34, end=45, tag='Phone_fax', doc_id='', ann_id='T2')
    ]


def test_surrogate_annotations():
    text = "De patient J. Jansen (e: j.jnsen@email.com, t: 06-12345678)"
    annotations = [
        Annotation(text='J. Jansen', start=11, end=20, tag='Name', doc_id='', ann_id='T0'),
        Annotation(text='j.jnsen@email.com', start=25, end=42, tag='Email', doc_id='', ann_id='T1'),
        Annotation(text='06-12345678', start=47, end=58, tag='Phone_fax', doc_id='', ann_id='T2')
    ]
    doc = Document(name='test_doc', text=text, annotations=annotations)

    surrogate_doc = list(surrogate_annotations([doc]))[0]

    assert len(surrogate_doc.annotations) == len(doc.annotations)
    assert re.match(r'De patient .* \(e: .*, t: .*\)', doc.text)

    for ann in surrogate_doc.annotations:
        assert surrogate_doc.text[ann.start:ann.end] == ann.text


def test_surrogate_annotations_errors_raise():
    doc = Document(
        name='test_doc',
        text='This document was written on INVALID_DATE.',
        annotations=[
            Annotation(text='INVALID_DATE', start=29, end=41, tag='Date', doc_id='', ann_id='T0')
        ]
    )

    with pytest.raises(ValueError, match=r'No valid surrogate for Annotation\(.*INVALID_DATE.*\)'):
        _ = list(surrogate_annotations([doc]))[0]


def test_surrogate_annotations_errors_ignore():
    original_doc = Document(
        name='test_doc',
        text='This document was written on INVALID_DATE.',
        annotations=[
            Annotation(text='INVALID_DATE', start=29, end=41, tag='Date', doc_id='', ann_id='T0')
        ]
    )

    gen = surrogate_annotations([original_doc], errors='ignore')
    surrogate_doc = list(gen)[0]
    assert surrogate_doc.text == original_doc.text
    assert surrogate_doc.annotations == original_doc.annotations
    assert surrogate_doc.annotations_without_surrogates == original_doc.annotations


def test_surrogate_annotations_errors_coerce():
    original_doc = Document(
        name='test_doc',
        text='This document was written on INVALID_DATE.',
        annotations=[
            Annotation(text='INVALID_DATE', start=29, end=41, tag='Date', doc_id='', ann_id='T0')
        ]
    )

    gen = surrogate_annotations([original_doc], errors='coerce')
    surrogate_doc = list(gen)[0]
    assert surrogate_doc.text == 'This document was written on [Date].'
    assert surrogate_doc.annotations == [
        Annotation(text='[Date]', start=29, end=35, tag='Date', doc_id='', ann_id='T0')
    ]
    assert surrogate_doc.annotations_without_surrogates == original_doc.annotations
