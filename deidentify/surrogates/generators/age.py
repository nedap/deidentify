import re

from .base import ExactMatchGenerator

AGE_REGEX = re.compile(r'\d+')

class AgeSurrogates(ExactMatchGenerator):

    def replace_one(self, annotation):
        for match in AGE_REGEX.finditer(annotation):
            age = int(match.group(0))
            if age > 89:
                age = 89
                annotation = re.sub(match.group(0), str(age), annotation)

        return annotation
