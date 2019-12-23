from deidentify.base import Annotation, Document
from deidentify.util import mask_annotations


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
