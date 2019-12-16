import pytest
from deidentify.base import Annotation


def test_annotation():
    ann_a = Annotation(text='test', start=12, end=15, tag='ABC', doc_id='123', ann_id='456')
    ann_b = Annotation(text='test', start=12, end=15, tag='ABC', doc_id='123', ann_id='456')
    ann_c = Annotation(text='test2', start=12, end=15, tag='ABC', doc_id='123', ann_id='456')

    assert ann_a == ann_b
    assert ann_a != ann_c

    with pytest.raises(AttributeError):
        ann_a.text = "Annotation should be immutable"

    # Annotation should also be hashable
    assert len(set([ann_a, ann_b, ann_c])) == 2
