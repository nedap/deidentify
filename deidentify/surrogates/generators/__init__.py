from functools import partial

from .base import RandomData, SurrogateGenerator, IdentityGenerator
from .identifier import IDSurrogates
from .phone import DIAL_CODES, DIAL_CODES_BY_LENGTH, PhoneFaxSurrogates
from .date import DateSurrogates, Date
from .age import AgeSurrogates
from .name import NameSurrogates, InitialsSurrogates
from .email import EmailSurrogates
from .url import URLSurrogates
from .location import LocationSurrogates
from .corpus_shuffle import RandomMappingSurrogates

from .name import random_char_mapping


class GeneratorFactory:

    def __init__(self, random_data):
        self.random_data = random_data

        self.firstname_char_mapping = random_char_mapping(random_data)
        self.lastname_char_mapping = random_char_mapping(random_data)

        self._factory = {
            'Name': partial(NameSurrogates,
                            random_data=random_data,
                            firstname_char_mapping=self.firstname_char_mapping,
                            lastname_char_mapping=self.lastname_char_mapping),
            'Initials': partial(InitialsSurrogates,
                                char_mapping=self.firstname_char_mapping),
            'Address': partial(LocationSurrogates, random_data=random_data),
            'Age': partial(AgeSurrogates, random_data=random_data),
            'Date': partial(DateSurrogates, random_data=random_data),
            'Phone_fax': partial(PhoneFaxSurrogates, random_data=random_data),
            'Email': partial(EmailSurrogates, random_data=random_data),
            'URL_IP': partial(URLSurrogates, random_data=random_data),
            'SSN': partial(IDSurrogates, random_data=random_data),
            'ID': partial(IDSurrogates, random_data=random_data),
            'Other': IdentityGenerator
        }

    def generator_for_tag(self, tag):
        return self._factory.get(tag, None)

    def shuffle_generator(self, choices):
        return partial(RandomMappingSurrogates, choices=choices, random_data=self.random_data)
