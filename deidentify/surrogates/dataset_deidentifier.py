from collections import defaultdict

from loguru import logger

from deidentify.surrogates.generators import GeneratorFactory, IdentityGenerator, RandomData


class Document:

    def __init__(self, annotations, text):
        annotations_grouped = defaultdict(list)
        annotations_text_grouped = defaultdict(list)
        for annotation in annotations:
            annotations_grouped[annotation.tag].append(annotation)
            annotations_text_grouped[annotation.tag].append(annotation.text)
        self._annotations_grouped = annotations_grouped
        self._annotations_text_grouped = annotations_text_grouped

        self._surrogates = defaultdict(list)
        self.text = text

    @property
    def tags(self):
        return self._annotations_grouped.keys()

    def annotations(self, tag):
        return self._annotations_grouped[tag]

    def annotations_text(self, tag):
        return self._annotations_text_grouped[tag]

    def add_surrogates(self, tag, surrogates):
        assert len(self.annotations(tag)) == len(surrogates)
        self._surrogates[tag] = surrogates

    def surrogates(self, tag):
        return self._surrogates[tag]

    def annotation_surrogate_pairs(self):
        """
        Get original annotations alongside with their surrogate. Annotations are sorted by
        ascending start offset.

        Returns
        -------
        annotations: iterable of deidentify.base.Annotation
            The original annotations
        surrogates: iterable of str
            The surrogates
        """
        annotations, surrogates = [], []
        for tag in self.tags:
            annotations += self.annotations(tag)
            surrogates += self.surrogates(tag)

        if annotations and surrogates:
            return zip(*sorted(zip(annotations, surrogates),
                               key=lambda annotation_surrogate: annotation_surrogate[0].start))
        return [], []


class DatasetDeidentifier:

    def __init__(self, random_data=None):
        if not random_data:
            random_data = RandomData(seed=45)
        self.random_data = random_data

    def generate_surrogates(self, documents):
        tag_choices = defaultdict(set)
        for doc in documents:
            for tag in doc.tags:
                tag_choices[tag].update(doc.annotations_text(tag))

        for doc in documents:
            generator_factory = GeneratorFactory(self.random_data)

            for tag in doc.tags:
                annotations_text = doc.annotations_text(tag)
                generator = generator_factory.generator_for_tag(tag)

                if not generator:
                    choices = tag_choices[tag] - set(annotations_text)

                    if not choices:
                        logger.warning(
                            f'Cannot apply corpus shuffle for tag={tag} as there are no choices. '
                            f'Ensure that there are at least two distinct {tag} annotations in'
                            f'separate documents. Will now fall-back to identity replacement.'
                        )
                        generator = IdentityGenerator
                    else:
                        generator = generator_factory.shuffle_generator(choices)

                surrogates = generator(annotations=annotations_text).replace_all()
                doc.add_surrogates(tag, surrogates)

        return documents
