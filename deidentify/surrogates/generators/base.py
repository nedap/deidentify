import string
from abc import ABC, abstractmethod
from random import Random


class RandomData:

    def __init__(self, seed=None):
        self.random = Random(seed)

    def digit(self, digits=string.digits):
        return self.choice(digits)

    def ascii_lowercase(self):
        return self.choice(string.ascii_lowercase)

    def ascii_uppercase(self):
        return self.choice(string.ascii_uppercase)

    def choice(self, seq):
        return self.random.choice(seq)

    def randint(self, a, b):
        return self.random.randint(a, b)

    def shuffle(self, seq):
        # random.shuffle performs in-place shuffling. Sampling without replacement is equivalent to
        # shuffling.
        return self.sample(seq, len(seq))

    def sample(self, seq, k, replacement=False):
        if replacement:
            return self.random.choices(seq, k=k)

        return self.random.sample(seq, k)


class SurrogateGenerator(ABC):

    def __init__(self, annotations, random_data=None):
        self.annotations = annotations

        if not random_data:
            random_data = RandomData()
        self.random_data = random_data

    @abstractmethod
    def replace_all(self):
        pass


class ExactMatchGenerator(SurrogateGenerator, ABC):

    def replace_all(self):
        cache = {}
        replaced = []

        for ann in self.annotations:
            if ann not in cache:
                cache[ann] = self.replace_one(ann)
            replaced.append(cache[ann])

        return replaced

    @abstractmethod
    def replace_one(self, annotation):
        pass


class IdentityGenerator(SurrogateGenerator):

    def replace_all(self):
        return self.annotations
