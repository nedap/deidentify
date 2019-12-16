from deidentify.base import Annotation, Document
from deidentify.evaluation.evaluator import ENTITY_TAG, Evaluator


def test_entity_level():
    gold = [
        Document(name='doc_a', text='', annotations=[Annotation('', 3, 6, 'MISC')]),
        Document(name='doc_b', text='', annotations=[Annotation('', 0, 2, 'PER')])
    ]

    predicted = [
        Document(name='doc_a', text='', annotations=[Annotation('', 2, 6, 'MISC')]),
        Document(name='doc_b', text='', annotations=[Annotation('', 0, 2, 'PER')])
    ]

    evaluator = Evaluator(gold, predicted)
    scores = evaluator.entity_level()
    assert scores.micro_avg_f_score() == 0.5
    assert scores.macro_avg_f_score() == 0.5
    assert scores.f_score('PER') == 1
    assert scores.f_score('MISC') == 0


def test_token_annotations():
    evaluator = Evaluator(gold=(), predicted=())
    doc = Document(name='doc_a', text='A B C D.', annotations=[
        Annotation('B C', 2, 5, 'PER'),
        Annotation('D.', 6, 8, 'ORG')
    ])

    assert evaluator.token_annotations(doc) == ['O', 'PER', 'PER', 'ORG']
    assert evaluator.token_annotations(doc, tag_blind=True) == ['O', 'ENT', 'ENT', 'ENT']


def test_token_level():
    text = 'A B C D.'

    gold_a = [Annotation('B C', 2, 5, 'PER')]
    gold_b = [Annotation('A', 0, 1, 'ORG'), Annotation('B', 2, 3, 'PER')]

    pred_a = [Annotation('B', 2, 3, 'PER'), Annotation('C', 4, 5, 'PER')]
    pred_b = [Annotation('A', 0, 1, 'ORG'), Annotation('B', 2, 3, 'ORG')]

    gold = [
        Document(name='doc_a', text=text, annotations=gold_a),
        Document(name='doc_b', text=text, annotations=gold_b)
    ]

    predicted = [
        Document(name='doc_a', text=text, annotations=pred_a),
        Document(name='doc_b', text=text, annotations=pred_b)
    ]

    evaluator = Evaluator(gold, predicted)
    scores = evaluator.token_level()
    assert scores.precision('PER') == 1
    assert scores.recall('PER') == 0.6667
    assert scores.f_score('PER') == 0.8

    assert scores.precision('ORG') == 0.5
    assert scores.recall('ORG') == 1
    assert scores.f_score('ORG') == 0.6667


def test_token_level_blind():
    gold_a = [Annotation('B C', 2, 5, 'PER')]
    gold_b = [Annotation('A', 0, 1, 'ORG')]

    pred_a = [Annotation('B', 2, 3, 'PER'), Annotation('C', 4, 5, 'PER')]
    pred_b = []

    gold = [
        Document(name='doc_a', text='A B C D.', annotations=gold_a),
        Document(name='doc_b', text='A B C D.', annotations=gold_b)
    ]

    predicted = [
        Document(name='doc_a', text='A B C D.', annotations=pred_a),
        Document(name='doc_b', text='A B C D.', annotations=pred_b)
    ]

    evaluator = Evaluator(gold, predicted)
    scores = evaluator.token_level_blind()
    assert scores.precision(ENTITY_TAG) == 1
    assert scores.recall(ENTITY_TAG) == 0.6667
    assert scores.f_score(ENTITY_TAG) == 0.8
