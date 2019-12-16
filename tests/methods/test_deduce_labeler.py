from deidentify.base import Annotation
from deidentify.methods.deduce.deduce_labeler import DeduceAnnotator

TEST_TEXT = u"Dit is stukje tekst met daarin de naam Jan Jansen. De patient J. Jansen (e: j.jnsen@email.com, t: 06-12345678) is 64 jaar oud en woonachtig in Utrecht. Hij werd op 10 oktober door arts Peter de Visser ontslagen van de kliniek van het UMCU."

ANNOTATOR = DeduceAnnotator(text=TEST_TEXT)


def test_annotation_content():
    assert ANNOTATOR.annotation_content('<LOCATIE Laverhof>') == 'Laverhof'


def test_annotation_tag():
    assert ANNOTATOR.annotation_tag('<LOCATIE Laverhof>') == 'LOCATIE'


def test_is_annotation():
    assert ANNOTATOR.is_annotation('<LOCATIE Laverhof>')
    assert not ANNOTATOR.is_annotation('This is not an annotation')
    assert not ANNOTATOR.is_annotation('This is also not an annotation <LOCATIE Laverhof>')


def test_flatten_tag_content():
    fac = ANNOTATOR.flatten_annotation_content
    assert fac('<PERSOON <LOCATIE Laverhof >Ondersteuning Thuis>') == 'Laverhof Ondersteuning Thuis'
    assert fac('Ondersteuning Thuis') == 'Ondersteuning Thuis'
    assert fac('<LOCATIE Laverhof> Ondersteuning <LOCATIE Thuis>') == 'Laverhof Ondersteuning Thuis'
    assert fac('<LOCATIE Laverhof>') == 'Laverhof'


def test_annotate_text():
    assert ANNOTATOR.annotated_text == "Dit is stukje tekst met daarin de naam <PERSOON Jan Jansen>. De <PERSOON patient J. Jansen> (e: <URL j.jnsen@email.com>, t: <TELEFOONNUMMER 06-12345678>) is <LEEFTIJD 64> jaar oud en woonachtig in <LOCATIE Utrecht>. Hij werd op <DATUM 10 oktober> door arts <PERSOON Peter de Visser> ontslagen van de kliniek van het <INSTELLING umcu>."


def test_annotations():
    actual = ANNOTATOR.annotations()

    assert actual == [
        Annotation('Jan Jansen', 39, 49, 'PERSOON'),
        Annotation('patient J. Jansen', 54, 71, 'PERSOON'),
        Annotation('j.jnsen@email.com', 76, 93, 'URL'),
        Annotation('06-12345678', 98, 109, 'TELEFOONNUMMER'),
        Annotation('64', 114, 116, 'LEEFTIJD'),
        Annotation('Utrecht', 143, 150, 'LOCATIE'),
        Annotation('10 oktober', 164, 174, 'DATUM'),
        Annotation('Peter de Visser', 185, 200, 'PERSOON'),
        # We explicitly check that the following annotation is included in it's correct form.
        # Deduce annotates UMCU as umcu. During annotation, we attempt to recover the original text.
        Annotation('UMCU', 234, 238, 'INSTELLING')
    ]
