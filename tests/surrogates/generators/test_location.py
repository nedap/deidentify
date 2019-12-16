from deidentify.surrogates.generators import LocationSurrogates, RandomData
from deidentify.surrogates.generators.location import (NUMBER_REGEX, ZIP_REGEX,
                                                       Location,
                                                       LocationDatabase,
                                                       _strip, parse_location)

from .util import RandomDataMock


def test_location_database():
    location_database = LocationDatabase()
    assert len(location_database.countries) >= 255
    assert 'Marokko' in location_database.countries
    assert 'Duitsland' in location_database.countries

    assert len(location_database.places) >= 2400
    assert 'Amsterdam' in location_database.places
    assert 'Enschede' in location_database.places
    assert 'Bennebroek' in location_database.places
    assert 'Haarlem' in location_database.places

    assert len(location_database.zip_codes) >= 452000
    assert '7141DC' in location_database.zip_codes

    assert len(location_database.streetnames) >= 127000
    assert 'Parallelweg' in location_database.streetnames
    assert 'Laan van Meerdervoort' in location_database.streetnames


def test_zip_regex():
    assert ZIP_REGEX.match('1234AB').group(0) == '1234AB'
    assert ZIP_REGEX.match('1234 AB').group(0) == '1234 AB'
    assert ZIP_REGEX.match('1234 ab').group(0) == '1234 ab'


def test_number_regex():
    assert NUMBER_REGEX.search('Parallelweg 122-3 a Groenlo').group(0) == '122-3 a'
    assert NUMBER_REGEX.search('Parallelweg 122-3 Groenlo').group(0) == '122-3'
    assert NUMBER_REGEX.search('Parallelweg 122A').group(0) == '122A'
    assert NUMBER_REGEX.search('Parallelweg 1').group(0) == '1'


def test_strip():
    assert _strip(' This is, a test, ') == 'This is, a test'
    assert _strip('This is, a test') == 'This is, a test'
    assert _strip('This is, a test,') == 'This is, a test'


def test_parse_location():
    # Case 1: ZIP Code => Left of ZIP is street, right is place and country
    assert parse_location('Parallelweg 2, 7141 DC Groenlo') == Location(
        raw='Parallelweg 2, 7141 DC Groenlo',
        country='',
        zip_code='7141 DC',
        place='Groenlo',
        street='Parallelweg',
        house_number='2')

    assert parse_location('Parallelweg 2, 7141 DC') == Location(
        raw='Parallelweg 2, 7141 DC',
        country='',
        zip_code='7141 DC',
        place='',
        street='Parallelweg',
        house_number='2')

    assert parse_location('7141DC') == Location(
        raw='7141DC', country='', zip_code='7141DC', place='', street='', house_number='')

    assert parse_location('7141 DC Groenlo') == Location(
        raw='7141 DC Groenlo', country='', zip_code='7141 DC', place='Groenlo', street='',
        house_number=''
    )

    assert parse_location('7141 DC te Haarlem Nederland') == Location(
        raw='7141 DC te Haarlem Nederland',
        country='Nederland',
        zip_code='7141 DC',
        place='te Haarlem',
        street='',
        house_number=''
    )

    # Case 2: No ZIP but number, split into left and right. Left of number (inclusive) is street,
    # right is place and country.
    assert parse_location('Parallelweg 2, Groenlo') == Location(
        raw='Parallelweg 2, Groenlo',
        country='',
        zip_code='',
        place='Groenlo',
        street='Parallelweg',
        house_number='2')

    assert parse_location('Parallelweg 2') == Location(
        raw='Parallelweg 2',
        country='',
        zip_code='',
        place='',
        street='Parallelweg',
        house_number='2')

    assert parse_location('Parallelweg 2A') == Location(
        raw='Parallelweg 2A',
        country='',
        zip_code='',
        place='',
        street='Parallelweg',
        house_number='2A')

    assert parse_location('Waterkant 11-3') == Location(
        raw='Waterkant 11-3',
        country='',
        zip_code='',
        place='',
        street='Waterkant',
        house_number='11-3')

    assert parse_location('Parallelweg 2 te Haarlem Nederland') == Location(
        raw='Parallelweg 2 te Haarlem Nederland',
        country='Nederland',
        zip_code='',
        place='te Haarlem',
        street='Parallelweg',
        house_number='2')

    # Case 3: no number, no ZIP code, split on road suffixes (e.g., weeg, straat). Left of suffix
    # is street, right is place and country.
    assert parse_location('Parallelweg Groenlo') == Location(
        raw='Parallelweg Groenlo',
        country='',
        zip_code='',
        place='Groenlo',
        street='Parallelweg',
        house_number='')

    assert parse_location('Parallelweg') == Location(
        raw='Parallelweg',
        country='',
        zip_code='',
        place='',
        street='Parallelweg',
        house_number='')

    assert parse_location('Parallelweg te Haarlem Nederland') == Location(
        raw='Parallelweg te Haarlem Nederland',
        country='Nederland',
        zip_code='',
        place='te Haarlem',
        street='Parallelweg',
        house_number='')

    assert parse_location('De singel te Haarlem Nederland') == Location(
        raw='De singel te Haarlem Nederland',
        country='Nederland',
        zip_code='',
        place='te Haarlem',
        street='De singel',
        house_number='')

    # Case 4: no number, no ZIP code, no street suffix => assume everything is a place,
    # except for names of countries
    assert parse_location('De diagonaal te Haarlem Nederland') == Location(
        raw='De diagonaal te Haarlem Nederland',
        country='Nederland',
        zip_code='',
        place='De diagonaal te Haarlem',
        street='',
        house_number='')

    assert parse_location('Groenlo') == Location(
        raw='Groenlo',
        country='',
        zip_code='',
        place='Groenlo',
        street='',
        house_number='')

    assert parse_location('Oostenrijk') == Location(
        raw='Oostenrijk',
        country='Oostenrijk',
        zip_code='',
        place='',
        street='',
        house_number='')

    assert parse_location('CARL MUCKSTRAAT') == Location(
        raw='CARL MUCKSTRAAT',
        country='',
        zip_code='',
        place='',
        street='CARL MUCKSTRAAT',
        house_number=''
    )

    assert parse_location('Waterkant 28-3, 7521PL Enschede') == Location(
        raw='Waterkant 28-3, 7521PL Enschede',
        country='',
        zip_code='7521PL',
        place='Enschede',
        street='Waterkant',
        house_number='28-3'
    )

    assert parse_location('Indonesië (Molukken)') == Location(
        raw='Indonesië (Molukken)',
        country='Indonesië',
        zip_code='',
        place='Molukken',
        street='',
        house_number=''
    )

    assert parse_location('De Giezen 15-002, 7461 BB') == Location(
        raw='De Giezen 15-002, 7461 BB',
        country='',
        zip_code='7461 BB',
        place='',
        street='De Giezen',
        house_number='15-002'
    )

    assert parse_location('Arnhem-Zuid') == Location(
        raw='Arnhem-Zuid',
        country='',
        zip_code='',
        place='Arnhem-Zuid',
        street='',
        house_number=''
    )

    assert parse_location('De Giezen 15-002, Arnhem-Zuid') == Location(
        raw='De Giezen 15-002, Arnhem-Zuid',
        country='',
        zip_code='',
        place='Arnhem-Zuid',
        street='De Giezen',
        house_number='15-002'
    )


def test_replace_all():
    locations = [
        ('7141DC', 'Groenlo', 'Parallelweg'),
    ]
    location_database = LocationDatabase(locations=locations)

    given_expected = [
        ('Waterkant 28-3, 7521PL Enschede', 'Parallelweg 11-1, 7141DC Groenlo'),
        ('Waterkant 28-3',                  'Parallelweg 11-1'),
        ('7521PL Enschede',                 '7141DC Groenlo'),
        ('7521 PL Enschede',                '7141 DC Groenlo'),
        ('Enschede',                        'Groenlo'),
        ('Arnhem-Zuid',                     'Groenlo'),
        # countries are be completely ignored during surrogate generation
        ('Oostenrijk',                      'Oostenrijk'),
        ('Duitsland',                       'Duitsland')
    ]

    annotations = [given for given, _ in given_expected]
    expected = [expected for _, expected in given_expected]

    location_surrogates = LocationSurrogates(annotations, location_database=location_database,
                                             random_data=RandomDataMock())
    surrogates = location_surrogates.replace_all()
    assert surrogates == expected
