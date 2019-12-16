import re

import deduce

from deidentify.base import Annotation

ANNOTATION_REGEX = re.compile(r'<([A-Z]+) (.*)>')


class DeduceAnnotator:

    def __init__(self, text):
        self.text = text
        self.annotated_text = deduce.annotate_text(self.text)

    @staticmethod
    def annotation_content(annotation):
        return ANNOTATION_REGEX.match(annotation).group(2)

    @staticmethod
    def annotation_tag(annotation):
        return ANNOTATION_REGEX.match(annotation).group(1)

    @staticmethod
    def is_annotation(part):
        return ANNOTATION_REGEX.match(part) is not None

    def flatten_annotation_content(self, annotation):
        """
        Recursively flattens nested annotations.

        Examples
        --------
        >>> from deidentify.methods.deduce import deduce_labeler
        >>> annotator = deduce_labeler.DeduceAnnotator(text='')
        >>> annotator.flatten_annotation_content('<PERSOON <LOCATIE Laverhof >Ondersteuning Thuis>')
        'Laverhof Ondersteuning Thuis'
        """
        splitted = deduce.utility.split_tags(annotation)

        text = ''
        for part in splitted:
            if self.is_annotation(part):
                text += self.flatten_annotation_content(self.annotation_content(part))
            else:
                text += part

        return text

    def annotations(self):
        """
        List of annotated PHI entities with their offset within the orginal (unannotated) text.
        """
        annotations = []

        text_parts = deduce.utility.split_tags(self.annotated_text)

        # Deduce denotes entities inline in form of <TYPE text>. We need to take this
        # into account when computing the character positions in the original text.
        original_text_pointer = 0
        ann_id = 0

        for part in text_parts:
            if self.is_annotation(part):
                tag = self.annotation_tag(part)
                # Disregard nested annotations. Nested content is considered to be part of the
                # parent annotation.
                ann_text = self.flatten_annotation_content(part)

                try:
                    # Deduce randomly removes spaces preceeding an annotation. We do a best effort
                    # to find back the entity in the original text. Matching is done relative to
                    # the deduce match, so that we do not capture unwanted text.
                    #
                    # Casing is ignored as deduce sometimes changes the original text.
                    # Example: deduce.annotate_text('UMCU') -> "<INSTELLING umcu>"
                    idx_match = self.text[original_text_pointer:].lower().index(ann_text.lower())
                except ValueError:
                    # Sometimes, Deduce changes the original annotation text. Example:
                    # gemeld door <PERSOON Jan van Jansen>
                    # gemeld door <PERSOON Jan Jan van Jansen>
                    #
                    # In those case, we cannot recover the annotation and skip to the next.
                    original_text_pointer += len(ann_text)
                    continue

                start_idx = idx_match + original_text_pointer
                end_idx = start_idx + len(ann_text)
                original_text_pointer = end_idx

                annotations.append(Annotation(
                    ann_id='T{}'.format(ann_id),
                    tag=tag,
                    text=self.text[start_idx:end_idx],
                    start=start_idx,
                    end=end_idx
                ))

                ann_id += 1
            else:
                original_text_pointer += len(part)

        return annotations
