import string

from .base import ExactMatchGenerator


class IDSurrogates(ExactMatchGenerator):

    def replace_one(self, annotation):
        randomized = ''
        for char in annotation:
            if char in string.ascii_lowercase:
                randomized += self.random_data.ascii_lowercase()
            elif char in string.ascii_uppercase:
                randomized += self.random_data.ascii_uppercase()
            elif char in string.digits:
                randomized += self.random_data.digit()
            else:
                randomized += char

        return randomized
