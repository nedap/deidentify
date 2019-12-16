from deidentify.surrogates.generators import URLSurrogates

from .util import RandomDataMock


def test_replace_all():
    annotations = [
        'www.abc.com/123-abc-6yz',
        'https://abc.com/123-abc-6yz',
        'http://abc.com/123-abc-6yz',
        'http://www.abc.com/123-abc-6yz',
        'http://abc.nl/123-abc-6yz',
        'abc.nl',
        'www.abc.nl',
    ]

    url_surrogates = URLSurrogates(annotations=annotations, random_data=RandomDataMock())

    assert url_surrogates.replace_all() == [
        'www.ccc.com/111-ccc-1cc',
        'https://ccc.com/111-ccc-1cc',
        'http://ccc.com/111-ccc-1cc',
        'http://www.ccc.com/111-ccc-1cc',
        'http://ccc.nl/111-ccc-1cc',
        'ccc.nl',
        'www.ccc.nl',
    ]
