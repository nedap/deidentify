from deidentify.surrogates.generators import AgeSurrogates


def test_replace_one():
    annotations = [
        '88 jarige',
        '24/25e',
        '2',
        '60',
        'patient is 92',
        '91 age',
        '90 jaar oud',
        '89 years',
        '101'
    ]
    age_surrogates = AgeSurrogates(annotations=annotations)

    annotations_replaced = age_surrogates.replace_all()
    assert annotations_replaced == [
        '88 jarige',
        '24/25e',
        '2',
        '60',
        'patient is 89',
        '89 age',
        '89 jaar oud',
        '89 years',
        '89'
    ]
