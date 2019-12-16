"""Generate random surrogates for names that are of the same syntactic pattern.

Examples:
- Daniel MT de Groot             => Jurrien HD Nguyen
- Dr. Annemarie van Heijer, Ph.D => Dr. Clara van der Linden, Ph.D

Algorithm:
1. Generate two random mappings for characters of the latin alphabet: one for firstnames and one
   for lastnames (e.g., A->E, B->F...). This helps to maintain continuity across documents by
   always replacing names and initials with the same character mapping.
2. For each name:
   2.1 Normalize the name into it's parts (title, first, middle, last, suffix) using `nameparser`
   2.2 Check lookup table if a surrogate for this name already exists. If not, continue.
   2.3 Extract the first letter of firstname, middle name and lastname, respectively.
   2.4 Map these letters using the appropriate character mapping from step 1.
   2.5 Lookup a random name that starts with the mapped character.
   2.6 Place (name: surrogate) mapping in the lookup list.

References:
- https://nameparser.readthedocs.io/en/latest/
- Stubbs, A., Uzuner, Ö., Kotfila, C., Goldstein, I., & Szolovits, P. (2015). Challenges in
  Synthesizing Surrogate PHI in Narrative EMRs. https://doi.org/10.1007/978-3-319-23633-9_27
"""
import re
import string
from collections import defaultdict
from os.path import dirname, join

import nameparser.config
import pandas as pd
from loguru import logger
from nameparser import HumanName
from unidecode import unidecode

from .base import ExactMatchGenerator, SurrogateGenerator

RESOURCES_PATH = join(dirname(__file__), 'resources')

# Add common Dutch titles for Mr. and Mrs.
nameparser.config.CONSTANTS.titles.add('mw', 'dhr', 'mevr', 'mr')
# Add common Dutch prepositions to prefixes such that they are parsed as part of last names as
# opposed to middle names.
# See: https://en.wikipedia.org/wiki/Dutch_name#Tussenvoegsels
PREPOSITIONS = ['van', 'den', 'v.d.', 'vd', 'de', 'der', "'t", 'ten', 'ter', 'at', 'op']
nameparser.config.CONSTANTS.prefixes.add(*PREPOSITIONS)

PREPOSITIONS_REGEX = re.compile(r'((?:{})\s)*'.format('|'.join(PREPOSITIONS)))
INITIALS_REGEX = re.compile(r'([A-Z]?\.?)+')


def random_char_mapping(random_data):
    """Generate a random mapping between for the characters of the lowercase ASCII alphabet.

    Parameters
    ----------
    random_data : deidentify.surrogates.RandomData
        The random operations provider.

    Returns
    -------
    dict(str: str)
        The random character mapping.
    """
    alphabet = string.ascii_lowercase
    shuffled = random_data.shuffle(alphabet)
    return dict(zip(alphabet, shuffled))


def _load_firstnames(filename):
    return pd.read_csv(filename, names=['name'])['name'].values


def _inverted_name_index(names, index_getter=lambda x: x[0]):
    index = defaultdict(list)
    for name in names:
        key = index_getter(name)
        key = NameDatabase.normalize_index_key(key)
        index[key].append(name)
    return index


class NameDatabase:

    def __init__(self, firstnames_male=None, firstnames_female=None, lastnames=None):
        """Provides access to the 10,000 most common Dutch firstnames/lastnames fetched from the
        Meertens Instituut (see: http://www.naamkunde.net).

        Name lists are stored in a form of "inverted index" where the key is the first letter of
        the firstname/lastname and the values are a list of names starting with this letter.

        Example for firstnames [Anne, Alieke, Jan, Thomas]:
        ```
            {
                'a': [Anne, Alieke],
                'j': [Jan],
                't': [Thomas]
            }
        ```

        Lastnames are stored as (prefix, lastname) tuples. Example: ('de', 'Groot').

        Parameters
        ----------
        firstnames_male : iterable of type `str`
            A list of male firstnames.
        firstnames_female : iterable of type `str`
            A list of female firstnames.
        lastnames : iterable of (str, str) tuples
            A list of lastname tuples in form of (prefix: str, lastname: str). Example: `('de', 'Groot')`.
        """
        if not firstnames_male:
            firstnames_male = _load_firstnames(join(RESOURCES_PATH, 'firstnames_male.txt'))
        self.__male_normalized = set(name.lower() for name in firstnames_male)
        self.male_index = _inverted_name_index(firstnames_male)

        if not firstnames_female:
            firstnames_female = _load_firstnames(join(RESOURCES_PATH, 'firstnames_female.txt'))
        self.__female_normalized = set(name.lower() for name in firstnames_female)
        self.female_index = _inverted_name_index(firstnames_female)

        if not lastnames:
            df_lastnames = pd.read_csv(join(RESOURCES_PATH, 'lastnames.csv'))
            df_lastnames.prefix.fillna('', inplace=True)
            lastnames = df_lastnames.apply(lambda row: (row['prefix'], row['name']), axis=1)

        # Given (prefix, lastname) tuple select first character of lastname and use as index
        def lastname_index_getter(prefix_lastname_tuple):
            return prefix_lastname_tuple[1][0]
        self.lastname_index = _inverted_name_index(lastnames, index_getter=lastname_index_getter)

    def gender_index_for_name(self, firstname):
        """Make a best-guess at the gender of the given firstname and returns the appropriate index
        name index.

        Performs a lookup in the firstname database. If name is not present in male index, it is
        assumed that the gender is female.

        Returns
        -------
        dict(str: [str])
            The name index correspoding to the gender of `firstname`.
        """
        if firstname.lower() in self.__male_normalized:
            return self.male_index
        return self.female_index

    @staticmethod
    def normalize_index_key(key):
        return unidecode(key).lower()


class InitialsSurrogates(ExactMatchGenerator):

    def __init__(self, annotations, char_mapping):
        super(InitialsSurrogates, self).__init__(annotations=annotations)
        self.char_mapping = char_mapping

    def replace_one(self, annotation):
        replacement = ''
        for initial in annotation:
            replacement_initial = self.char_mapping.get(initial.lower(), initial)
            # restore casing of original initial
            if initial.islower():
                replacement_initial = replacement_initial.lower()
            elif initial.isupper():
                replacement_initial = replacement_initial.upper()
            replacement += replacement_initial
        return replacement


class NameSurrogates(SurrogateGenerator):

    def __init__(self, annotations, random_data, firstname_char_mapping, lastname_char_mapping,
                 name_database=NameDatabase()):
        super(NameSurrogates, self).__init__(annotations=annotations, random_data=random_data)

        self.firstname_char_mapping = firstname_char_mapping
        self.lastname_char_mapping = lastname_char_mapping
        self.name_database = name_database
        self.initials_surrogates = InitialsSurrogates(annotations=[],
                                                      char_mapping=firstname_char_mapping)

    @staticmethod
    def normalize_name(annotation):
        return HumanName(annotation)

    @staticmethod
    def remove_prepositions(lastname):
        return PREPOSITIONS_REGEX.sub('', lastname)

    @staticmethod
    def is_initials(part_of_name):
        return not INITIALS_REGEX.sub('', part_of_name)

    def _get_surrogate_name(self, index, index_key, char_mapping):
        """Retrieve random surrogate from the given index according to a character mapped index.

        Index keys are normalized by transliterating unicode characters to their ascii equivalent
        and lowercasing (e.g., Ö => o).

        Parameters
        ----------
        index : dict(str: [str])
            The name index to retrieve a random name from. The first letter of the values equals
            the index key.
        index_key : str
            The first letter of a name.
        char_mapping : dict(str: str)
            A random character mapping.

        Returns
        -------
        str
            A random name starting with the value of `char_mapping[index_key]`.
        """
        index_key = self.name_database.normalize_index_key(index_key)
        first_letter_surrogate = char_mapping[index_key]
        return self.random_data.choice(index[first_letter_surrogate])

    @staticmethod
    def restore_case(original_char, new_string):
        if original_char.islower():
            return new_string[0].lower() + new_string[1:]

        return new_string[0].upper() + new_string[1:]

    def surrogate_firstname(self, firstname):
        name_index = self.name_database.gender_index_for_name(firstname)
        first_letter = firstname[0]
        return self._get_surrogate_name(name_index, first_letter, self.firstname_char_mapping)

    def surrogate_lastname(self, lastname):
        lastname = self.remove_prepositions(lastname)
        first_letter = lastname[0]
        return self._get_surrogate_name(self.name_database.lastname_index,
                                        first_letter, self.lastname_char_mapping)

    @staticmethod
    def cached_surrogate(cache, name_string, replacement_generator):
        """Generate a new surrogate for the given name or use an existing one if it already exist.

        Parameters
        ----------
        cache : dict(str: str)
            Lookup table of already replaced names. Keys are original names and values are
            surrogates.
        name_string : str
            The name to generate a replacement for
        replacement_generator : callable accepting `name_string`
            A callable that generates a new surrogate for `name_string`, in case no previous
            replacement exists.

        Returns
        -------
        str
            The surrogate name.

        """
        replacement = cache.get(name_string.lower(), None)
        if not replacement:
            replacement = replacement_generator(name_string)
            cache[name_string.lower()] = replacement
        return replacement

    @staticmethod
    def strict_replace(part, replacement, whole):
        # initials may end on ., so matching on a word boundary \b is insufficient.
        # If we match on \W, we need to re-insert this in the substitute.
        fmt = r'\b(?:{})(\W|\b)'.format(part)
        return re.sub(fmt, replacement + r'\1', whole)

    def _replace_name(self, annotation, firstname_mapping, lastname_mapping):
        new_name = annotation
        name = self.normalize_name(annotation)

        if name.first:
            if self.is_initials(name.first):
                replacement = self.initials_surrogates.replace_one(name.first)
            else:
                replacement = self.cached_surrogate(firstname_mapping,
                                                    name.first,
                                                    self.surrogate_firstname)
                replacement = self.restore_case(name.first[0], replacement)
            new_name = self.strict_replace(part=name.first, replacement=replacement, whole=new_name)

        if name.middle:
            replacement = ''
            parts = name.middle.split()
            for i, part in enumerate(parts):
                if self.is_initials(part):
                    replacement += self.initials_surrogates.replace_one(part)
                else:
                    # If part is not an initial, we assume it is a middle name
                    part_replacement = self.cached_surrogate(firstname_mapping,
                                                             part,
                                                             self.surrogate_firstname)
                    replacement += self.restore_case(part[0], part_replacement)
                if i < len(parts) - 1:
                    replacement += ' '
            new_name = self.strict_replace(part=name.middle, replacement=replacement,
                                           whole=new_name)

        if name.last:
            original_lastname = self.remove_prepositions(name.last)
            replacement = self.cached_surrogate(lastname_mapping,
                                                name.last,
                                                self.surrogate_lastname)
            prefix, lastname = replacement
            lastname = self.restore_case(original_lastname[0], lastname)
            if prefix:
                replacement = prefix + ' ' + lastname
            else:
                replacement = lastname
            new_name = self.strict_replace(part=name.last, replacement=replacement, whole=new_name)

        assert new_name != annotation
        return new_name

    def replace_all(self):
        firstname_mapping = {}
        lastname_mapping = {}

        replaced = []
        for annotation in self.annotations:
            # TODO: Add an annotation object that encapsules automatic replacement errors
            new_name = None
            try:
                new_name = self._replace_name(annotation, firstname_mapping, lastname_mapping)
            except (AssertionError, KeyError):
                logger.opt(exception=False).debug('Could not process name {}'.format(annotation))
            replaced.append(new_name)

        return replaced
