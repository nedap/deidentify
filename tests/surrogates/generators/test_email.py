from deidentify.surrogates.generators import EmailSurrogates

from .util import RandomDataMock


def test_replace_all():
    annotations = [
        'jan.janssen@gmail.com',
        'jan.janssen@com.com',
        'Abc-aBc@com3.com'
    ]

    email_surrogates = EmailSurrogates(annotations=annotations, random_data=RandomDataMock())

    assert email_surrogates.replace_all() == [
        'ccc.ccccccc@ccccc.com',
        'ccc.ccccccc@ccc.com',
        'Ccc-cCc@ccc1.com'
    ]
