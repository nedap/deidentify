import re
from collections import namedtuple
from os.path import dirname, join

import pandas as pd

from .base import SurrogateGenerator
from .identifier import IDSurrogates

RESOURCES_PATH = join(dirname(__file__), 'resources')
# Regex to recognize house numbers (e.g., 7A or 123-4 or 123 A)
NUMBER_REGEX = re.compile(r'(?:\d+-?)+(?:\w|\s\w\b)?', re.IGNORECASE)
ZIP_REGEX = re.compile(r'[0-9]{4}\s?[a-z]{2}', re.IGNORECASE)
# See Deduce:
# https://github.com/vmenger/deduce/blob/dd90ee918700c55658f773926d6d9c609b03c1c4/deduce/annotate.py#L473
STREET_REGEX = re.compile(
    r'\w*(straat|laan|hof|plein|plantsoen|gracht|kade|weg|burg|strjitte|veld|'
    'steeg|pad|dijk|baan|dam|dreef|kade|markt|park|plantsoen|singel|bolwerk)', re.IGNORECASE
)

Location = namedtuple('Location', ['raw', 'country', 'zip_code', 'place', 'street', 'house_number'])


class LocationDatabase:

    def __init__(self, countries=None, locations=None):
        def unique(seq):
            return sorted(list(set(seq)))

        if countries:
            countries = pd.DataFrame(countries, columns=['id', 'value'])
        else:
            countries = pd.read_csv(join(RESOURCES_PATH, 'country.csv'))
        self.countries = unique(countries['value'])
        self.countries_normalized = unique(country.lower() for country in self.countries)

        if locations:
            locations = pd.DataFrame(locations, columns=['postcode', 'plaats', 'straat'])
        else:
            locations = pd.read_csv(join(RESOURCES_PATH, 'postcodes-zones.csv'))

        self.locations = locations
        self.places = unique(locations['plaats'])
        self.zip_codes = unique(locations['postcode'])
        self.streetnames = unique(locations['straat'])


_LOCATION_DATABASE = LocationDatabase()


def _strip(string):
    """Remove non-word characters from either end of the string.

    Like `str.strip` but also removing punctuation.
    """
    string = re.sub(r'^\W*', '', string)
    string = re.sub(r'\W*$', '', string)
    return string


def _split_location(regex, location_string, include_match_in_left=True):
    match = regex.search(location_string)
    if match:
        if include_match_in_left:
            left = location_string[:match.end()]
        else:
            left = location_string[:match.start()]
        right = location_string[match.end():]
        return left, right, match
    return None


def parse_location(location_string, location_databse=_LOCATION_DATABASE):
    street, zip_code, country, house_number, place = '', '', '', '', ''

    zip_match = _split_location(ZIP_REGEX, location_string, include_match_in_left=False)
    number_match = _split_location(NUMBER_REGEX, location_string)
    street_match = _split_location(STREET_REGEX, location_string)

    if zip_match:
        street, place, match = zip_match
        zip_code = match.group(0)
    elif number_match:
        street, place, _ = number_match
    elif street_match:
        street, place, _ = street_match
    else:
        place = location_string

    house_number_match = NUMBER_REGEX.search(street)
    if house_number_match:
        house_number = house_number_match.group(0)
        street = street.replace(house_number, '')

    for token in place.split():
        # This assumes that a country is only a single token.
        if token.lower() in location_databse.countries_normalized:
            country = token

    place = place.replace(country, '')

    return Location(
        raw=location_string,
        country=_strip(country),
        zip_code=_strip(zip_code),
        place=_strip(place),
        street=_strip(street),
        house_number=_strip(house_number)
    )


class LocationSurrogates(SurrogateGenerator):

    def __init__(self, annotations, random_data=None, location_database=_LOCATION_DATABASE):
        super(LocationSurrogates, self).__init__(annotations, random_data)
        self.location_database = location_database
        self.id_surrogates = IDSurrogates(annotations=[], random_data=random_data)

    @staticmethod
    def cached_surrogate(cache, location_string, replacement_generator):
        replacement = cache.get(location_string.lower(), None)
        if not replacement:
            replacement = replacement_generator(location_string)
            cache[location_string.lower()] = replacement
        return replacement

    def surrogate_zip(self, original_zip):
        random_zip = self.random_data.choice(self.location_database.zip_codes)
        numbers = random_zip[:4]
        letters = random_zip[4:]

        surrogate = re.sub(r'[0-9]{4}', numbers, original_zip)
        surrogate = re.sub(r'[a-zA-Z]{2}', letters, surrogate)
        return surrogate

    def surrogate_place(self, _):
        return self.random_data.choice(self.location_database.places)

    def surrogate_street(self, _):
        return self.random_data.choice(self.location_database.streetnames)

    def surrogate_housenumber(self, original_house_number):
        return self.id_surrogates.replace_one(original_house_number)

    def replace_all(self):
        replaced = []

        zip_cache = {}
        place_cache = {}
        street_cache = {}
        house_number_cache = {}

        for annotation in self.annotations:
            new_location = annotation
            location = parse_location(annotation)

            if location.zip_code:
                replacement = self.cached_surrogate(zip_cache,
                                                    location.zip_code,
                                                    self.surrogate_zip)
                new_location = new_location.replace(location.zip_code, replacement)

            if location.place:
                replacement = self.cached_surrogate(place_cache,
                                                    location.place,
                                                    self.surrogate_place)
                new_location = new_location.replace(location.place, replacement)

            if location.street:
                replacement = self.cached_surrogate(street_cache,
                                                    location.street,
                                                    self.surrogate_street)
                new_location = new_location.replace(location.street, replacement)

            if location.house_number:
                replacement = self.cached_surrogate(house_number_cache,
                                                    location.house_number,
                                                    self.surrogate_housenumber)
                new_location = new_location.replace(location.house_number, replacement)

            replaced.append(new_location)

        return replaced
