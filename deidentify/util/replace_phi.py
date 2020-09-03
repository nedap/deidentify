from typing import Callable, List

from deidentify.base import Annotation, Document
from deidentify.surrogates.dataset_deidentifier import DatasetDeidentifier
from deidentify.surrogates.dataset_deidentifier import Document as SurrogateDocument
from deidentify.surrogates.rewrite_dataset import apply_surrogates
from deidentify.surrogates.generators import RandomData


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


def surrogate_annotations(docs: List[Document], seed=42) -> List[Document]:
    random_data = RandomData(seed=seed)
    dataset_deidentifier = DatasetDeidentifier(random_data=random_data)

    surrogate_docs = [SurrogateDocument(doc.annotations, doc.text) for doc in docs]
    surrogate_docs = dataset_deidentifier.generate_surrogates(documents=surrogate_docs)

    for doc in surrogate_docs:
        annotations, surrogates = doc.annotation_surrogate_pairs()
        rewritten_text, rewritten_annotations = apply_surrogates(doc.text, annotations, surrogates)
        yield Document(name='', text=rewritten_text, annotations=rewritten_annotations)
