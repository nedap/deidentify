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


def surrogate_annotations(docs: List[Document], seed=42, errors='raise') -> List[Document]:
    """Replaces PHI annotations in documents with random surrogates.

    Parameters
    ----------
    seed : int
        Set this seed to make the random generation deterministic.
    errors : str {'ignore', 'raise', 'coerce'}, default 'raise'
        - If 'raise',  errors during surrogate generation will raise an exception.
        - If 'ignore', failing annotations are skipped (they and PHI remains in text)
        - If 'coerce', failing annotations are replaced with pattern `[annotation.tag]`

    Returns
    -------
    List[Document]
        A copy of `docs` with with text and annotations rewritten to their surrogates.

        If errors is 'ignore' or 'coerce', an extra property of type List is added to the returned
        documents (`Document.annotations_without_surrogates`), which includes annotations of the
        *input document* that could not be replaced with a surrogate.

    """
    random_data = RandomData(seed=seed)
    dataset_deidentifier = DatasetDeidentifier(random_data=random_data)

    surrogate_docs = [SurrogateDocument(doc.annotations, doc.text) for doc in docs]
    surrogate_docs = dataset_deidentifier.generate_surrogates(documents=surrogate_docs)

    for doc in surrogate_docs:
        annotations, surrogates = doc.annotation_surrogate_pairs()
        doc_rewritten = apply_surrogates(doc.text, annotations, surrogates, errors=errors)
        yield doc_rewritten
