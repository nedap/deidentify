from .base import ExactMatchGenerator
from .identifier import IDSurrogates

class EmailSurrogates(ExactMatchGenerator):
    """Generates a random email by replacing each character with a random character of the same
    class. The top-level domain (TLD) is preserved.

    This strategy results in unrealistic email addresses. For example jan.janssen@gmail.com is
    replaced with iba.qbkbaase@uync.com
    """

    def __init__(self, annotations, random_data=None):
        super(EmailSurrogates, self).__init__(annotations, random_data)

        self.id_surrogates = IDSurrogates(annotations=[], random_data=random_data)

    def replace_one(self, annotation):
        tld_index = annotation.rfind('.')
        tld = annotation[tld_index:]
        replacement = self.id_surrogates.replace_one(annotation[:tld_index])
        return replacement + tld
