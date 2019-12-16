from .base import SurrogateGenerator


class RandomMappingSurrogates(SurrogateGenerator):

    def __init__(self, annotations, choices, random_data=None):
        super(RandomMappingSurrogates, self).__init__(annotations, random_data)
        # ensure choices is indexable and sort for reproducibility
        self.choices = sorted(list(choices))
        self.unique_annotations = sorted(list(set(annotations)))

    def replace_all(self):

        k = len(self.unique_annotations)
        replacement = k > len(self.choices)
        target_surrogates = self.random_data.sample(self.choices, k=k, replacement=replacement)

        mapping = {}
        for original, surrogate in zip(self.unique_annotations, target_surrogates):
            mapping[original] = surrogate

        replaced = []
        for annotation in self.annotations:
            replaced.append(mapping[annotation])
        return replaced
