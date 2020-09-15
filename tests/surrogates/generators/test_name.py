import collections
import string

from deidentify.surrogates.generators import (InitialsSurrogates,
                                              NameSurrogates, RandomData)
from deidentify.surrogates.generators.name import (NameDatabase,
                                                   random_char_mapping)


def list_equal(a, b):
    return collections.Counter(a) == collections.Counter(b)


class RandomDataMock(RandomData):

    def choice(self, seq):
        return seq[1]


def _name_database():
    firstnames_male = ['Jonatan', 'Joep', 'Stevan', 'Anne', 'Lucas']
    firstnames_female = ['Celina', 'Anne', 'Caroline', 'Janine', 'Özlem', 'Şeyda', 'Şerife']
    lastnames = [('', 'Heijermanns'), ('', 'Heijer'), ('', 'Lammers'), ('van der', 'Linden')]

    return NameDatabase(firstnames_male=firstnames_male,
                        firstnames_female=firstnames_female,
                        lastnames=lastnames)


def test_name_database():
    name_database = _name_database()

    assert list_equal(name_database.male_index.keys(), ['j', 's', 'a', 'l'])
    assert list_equal(name_database.male_index['j'], ['Jonatan', 'Joep'])
    assert list_equal(name_database.male_index['s'], ['Stevan'])
    assert list_equal(name_database.male_index['a'], ['Anne'])
    assert list_equal(name_database.male_index['l'], ['Lucas'])

    assert list_equal(name_database.female_index.keys(), ['a', 'c', 'j', 'o', 's'])
    assert list_equal(name_database.female_index['a'], ['Anne'])
    assert list_equal(name_database.female_index['c'], ['Celina', 'Caroline'])
    assert list_equal(name_database.female_index['j'], ['Janine'])
    assert list_equal(name_database.female_index['o'], ['Özlem'])
    assert list_equal(name_database.female_index['s'], ['Şeyda', 'Şerife'])

    assert list_equal(name_database.lastname_index.keys(), ['h', 'l'])
    assert list_equal(name_database.lastname_index['h'], [('', 'Heijermanns'), ('', 'Heijer')])
    assert list_equal(name_database.lastname_index['l'], [('', 'Lammers'), ('van der', 'Linden')])


def test_name_database_meertens():
    name_database = NameDatabase()
    assert sum(map(len, name_database.male_index.values())) >= 4000
    assert sum(map(len, name_database.female_index.values())) >= 4000
    assert sum(map(len, name_database.lastname_index.values())) >= 9900

    assert set(string.ascii_lowercase).issubset(set(name_database.male_index.keys()))
    assert set(string.ascii_lowercase).issubset(set(name_database.female_index.keys()))
    assert set(string.ascii_lowercase).issubset(set(name_database.lastname_index.keys()))


def test_gender_index_for_name():
    name_database = _name_database()
    assert name_database.gender_index_for_name('Celina') == name_database.female_index
    assert name_database.gender_index_for_name('Jonatan') == name_database.male_index
    assert name_database.gender_index_for_name('jonAtan') == name_database.male_index
    assert name_database.gender_index_for_name('unknown-name') == name_database.female_index


def test_random_char_mapping():
    random_data = RandomData()

    random_mapping = random_char_mapping(random_data=random_data)
    assert set(random_mapping.keys()) == set(string.ascii_lowercase)
    assert set(random_mapping.values()) == set(string.ascii_lowercase)


def test_normalize_name():
    normalize_name = NameSurrogates.normalize_name
    name = normalize_name('Lucas de Groot')
    assert name.first == 'Lucas'
    assert name.last == 'de Groot'

    name = normalize_name('Jasmin Dekker')
    assert name.first == 'Jasmin'
    assert name.last == 'Dekker'

    name = normalize_name('Lucas v.d. Veen')
    assert name.first == 'Lucas'
    assert name.last == 'v.d. Veen'

    name = normalize_name('Lucas vd Veen')
    assert name.first == 'Lucas'
    assert name.last == 'vd Veen'

    name = normalize_name('Dhr. Lucas F.A. de Groot, Ph.D.')
    assert name.title == 'Dhr.'
    assert name.first == 'Lucas'
    assert name.middle == 'F.A.'
    assert name.last == 'de Groot'
    assert name.suffix == 'Ph.D.'

    name = normalize_name('Daniel Markus Thomas de Groot')
    assert name.title == ''
    assert name.first == 'Daniel'
    assert name.middle == 'Markus Thomas'
    assert name.last == 'de Groot'

    name = normalize_name('Daniel Markus Thomas P.F.J. de Groot')
    assert name.title == ''
    assert name.first == 'Daniel'
    assert name.middle == 'Markus Thomas P.F.J.'
    assert name.last == 'de Groot'

    name = normalize_name('van Janssen, Jan')
    assert name.title == ''
    assert name.first == 'Jan'
    assert name.middle == ''
    assert name.last == 'van Janssen'

    name = normalize_name('Jan van Janssen')
    assert name.title == ''
    assert name.first == 'Jan'
    assert name.middle == ''
    assert name.last == 'van Janssen'

    name = normalize_name('J. Janssen')
    assert name.title == ''
    assert name.first == 'J.'
    assert name.middle == ''
    assert name.last == 'Janssen'

    name = normalize_name('J. F. Janssen')
    assert name.title == ''
    assert name.first == 'J.'
    assert name.middle == 'F.'
    assert name.last == 'Janssen'

    name = normalize_name('D. de Groot')
    assert name.title == ''
    assert name.first == 'D.'
    assert name.middle == ''
    assert name.last == 'de Groot'

    # This is a malformatted name where parsing fails. We shold still handle it gracefully.
    name = normalize_name('Ludo)Enckels')
    assert name.first == 'Ludo)Enckels'

def test_strict_replace():
    sp = NameSurrogates.strict_replace
    assert sp(part='Jan', replacement='Peter', whole='van Janssen, Jan') == 'van Janssen, Peter'
    assert sp(part='Ludo)Enckels', replacement='Peter', whole='Ludo)Enckels') == 'Peter'


def test_surrogate_firstname():
    name_surrogates = NameSurrogates(annotations=[],
                                     random_data=RandomDataMock(),
                                     firstname_char_mapping={'l': 'j', 'j': 'c', 'o': 's'},
                                     lastname_char_mapping={},
                                     name_database=_name_database())

    name = name_surrogates.normalize_name('Lucas de Groot')
    assert name_surrogates.surrogate_firstname(name.first) == 'Joep'

    name = name_surrogates.normalize_name('Janine Dekker')
    assert name_surrogates.surrogate_firstname(name.first) == 'Caroline'

    name = name_surrogates.normalize_name('Özlem Dekker')
    assert name_surrogates.surrogate_firstname(name.first) == 'Şerife'

    name = name_surrogates.normalize_name('Özlem Dekker')
    assert name_surrogates.surrogate_firstname(name.first) == 'Şerife'

    name = name_surrogates.normalize_name('Lucas de Groot')
    assert name_surrogates.surrogate_firstname(name.first) == 'Joep'


def test_remove_prepositions():
    remove_prepositions = NameSurrogates.remove_prepositions
    assert remove_prepositions('v.d. Groot') == 'Groot'
    assert remove_prepositions('van den Groot') == 'Groot'
    assert remove_prepositions('Groot') == 'Groot'
    assert remove_prepositions('Grooter') == 'Grooter'


def test_surrogate_lastname():
    name_surrogates = NameSurrogates(annotations=[],
                                     random_data=RandomDataMock(),
                                     firstname_char_mapping={},
                                     lastname_char_mapping={'g': 'h', 'd': 'l'},
                                     name_database=_name_database())

    name = name_surrogates.normalize_name('Lucas de Groot')
    assert name_surrogates.surrogate_lastname(name.last) == ('', 'Heijer')

    name = name_surrogates.normalize_name('Lucas de groot')
    assert name_surrogates.surrogate_lastname(name.last) == ('', 'Heijer')

    name = name_surrogates.normalize_name('Janine Dekker')
    assert name_surrogates.surrogate_lastname(name.last) == ('van der', 'Linden')

    name = name_surrogates.normalize_name('Janine Dekker')
    assert name_surrogates.surrogate_lastname(name.last) == ('van der', 'Linden')


def test_is_initials():
    is_initials = NameSurrogates.is_initials
    assert is_initials('P')
    assert is_initials('P.')
    assert is_initials('PF')
    assert is_initials('P.F.')
    assert is_initials('PFJ')
    assert is_initials('P.F.J.')
    assert not is_initials('Ad')
    assert not is_initials('ad')
    assert not is_initials('thomas')
    assert not is_initials('Thomas')


def test_replace_all():
    male = ['Daniel', 'Markus', 'Thomas', 'Jan', 'Jurrien', 'Harm', 'Harmen', 'Damien', 'Dano']
    female = ['Annemarie', 'Caroline', 'Clara']
    lastnames = [('van', 'Leuween'), ('van der', 'Linden'), ('', 'Nieuwenhuis'), ('', 'Nguyen')]

    name_database = NameDatabase(firstnames_male=male,
                                 firstnames_female=female,
                                 lastnames=lastnames)

    firstname_char_mapping = {
        'a': 'c',
        'd': 'j',
        'm': 'h',
        't': 'd',
    }

    lastname_char_mapping = {
        'h': 'l',
        'g': 'n'
    }

    # pylint: disable=C0326
    given_expected = [
        ('Dr. Annemarie van Heijer, Ph.D',   'Dr. Clara van der Linden, Ph.D'),
        ('Annemarie van Heijer',             'Clara van der Linden'),
        ('annemarie',                        'clara'),
        ('Daniel de groot',                  'Jurrien nguyen'),
        ('Daniel',                           'Jurrien'),
        ('D. de Groot',                      'J. Nguyen'),
        ('Daniel markus thomas de Groot',    'Jurrien harmen damien Nguyen'),
        ('Daniel MT de Groot',               'Jurrien HD Nguyen'),
        ('Daniel M.T. de Groot',             'Jurrien H.D. Nguyen')
    ]
    annotations = (given for given, _ in given_expected)
    expected = [expected for _, expected in given_expected]

    name_surrogates = NameSurrogates(annotations=annotations,
                                     random_data=RandomDataMock(),
                                     firstname_char_mapping=firstname_char_mapping,
                                     lastname_char_mapping=lastname_char_mapping,
                                     name_database=name_database)

    surrogates = name_surrogates.replace_all()
    assert surrogates == expected


def test_replace_all_with_substring():
    name_database = NameDatabase()

    firstname_char_mapping = {
        'j': 'd'
    }

    lastname_char_mapping = {
        'j': 'n'
    }

    annotations = ['Jan Janosh janssen']
    name_surrogates = NameSurrogates(annotations=annotations,
                                     random_data=RandomDataMock(),
                                     firstname_char_mapping=firstname_char_mapping,
                                     lastname_char_mapping=lastname_char_mapping,
                                     name_database=name_database)

    surrogates = name_surrogates.replace_all()
    first, middle, last = surrogates[0].split()
    assert first[0] == 'D'
    assert middle[0] == 'D'
    assert last[0] == 'n'


def test_initials_surrogates():
    annotations = [
        'T.M.J.',
        'TM',
        'O',
        'T.',
        't.',
        't.M.j.'
    ]

    char_mapping = {'t': 'f', 'm': 'a', 'j': 'u', 'o': 'p'}

    initials_surrogates = InitialsSurrogates(annotations=annotations,
                                             char_mapping=char_mapping)
    assert initials_surrogates.replace_all() == [
        'F.A.U.',
        'FA',
        'P',
        'F.',
        'f.',
        'f.A.u.'
    ]
