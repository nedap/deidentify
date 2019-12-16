from deidentify.surrogates.generators import RandomMappingSurrogates
from collections import Counter

def test_random_mapping_surrogates_replace_all():
    annotations = [
        'A',
        'B',
        'B',
        'C',
        'D'
    ]

    choices = [
        'E',
        'F',
        'G',
        'H',
        'I'
    ]

    rms = RandomMappingSurrogates(annotations, choices)

    for _ in range(100):
        replaced = rms.replace_all()
        assert len(replaced) == len(annotations)
        assert all(e in choices for e in replaced)

        counts = Counter(replaced)
        assert counts[replaced[0]] == 1
        assert counts[replaced[1]] == 2
        assert counts[replaced[2]] == 2
        assert replaced[1] == replaced[2]
        assert counts[replaced[3]] == 1
        assert counts[replaced[4]] == 1
