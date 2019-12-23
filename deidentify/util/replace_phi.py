from typing import Callable

from deidentify.base import Annotation, Document


def _uppercase_formatter(annotation: Annotation):
    return '[{}]'.format(annotation.tag.upper())


def mask_annotations(document: Document,
                     replacement_formatter: Callable[[Annotation], str] = _uppercase_formatter
                     ) -> Document:
    """Utility function to replace sensitive PHI spans with a placeholder.

    Parameters
    ----------
    document : Document
        The document whose PHI annotations should be replaced.
    replacement_formatter : Callable[[Annotation], str]
        A callable that can be used to configure the formatting of the replacement.
        The default formatter replaces an annotation with `[annotation.tag.upper()]`.

    Returns
    -------
    Document
        The document with masked annotations.
    """
    # Amount of characters by which start point of annotation is adjusted
    # Positive shift if replacement is longer than original annotation
    # Negative shift if replacement is shorter
    shift = 0

    original_text_pointer = 0
    text_rewritten = ''
    annotations_rewritten = []

    for annotation in document.annotations:
        replacement = replacement_formatter(annotation)
        part = document.text[original_text_pointer:annotation.start]

        start = annotation.start + shift
        end = start + len(replacement)
        shift += len(replacement) - len(annotation.text)

        text_rewritten += part + replacement
        original_text_pointer = annotation.end
        annotations_rewritten.append(annotation._replace(
            start=start,
            end=end,
            text=replacement
        ))

    text_rewritten += document.text[original_text_pointer:]
    return Document(name=document.name, text=text_rewritten, annotations=annotations_rewritten)
