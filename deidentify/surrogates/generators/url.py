import re
from .base import ExactMatchGenerator
from .identifier import IDSurrogates

TLDS = ['org', 'com', 'nl', 'de', 'be', 'co.uk', 'gov', 'net', 'edu', 'care']
URL_ELEMENTS_REGEX = re.compile(r'(https?|www\.|\.(?:{}))'.format('|'.join(TLDS)))


class URLSurrogates(ExactMatchGenerator):

    def __init__(self, annotations, random_data=None):
        super(URLSurrogates, self).__init__(annotations, random_data)
        self.id_surrogates = IDSurrogates(annotations=[], random_data=random_data)

    def replace_one(self, annotation):
        url_components = URL_ELEMENTS_REGEX.finditer(annotation)

        replacement = self.id_surrogates.replace_one(annotation)
        for match in url_components:
            replacement = replacement[:match.start()] + match.group(1) + replacement[match.end():]

        return replacement
