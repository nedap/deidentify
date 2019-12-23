"""Utility methods to convert between standoff and BIO format.
"""

from collections import defaultdict, namedtuple
from typing import List, Tuple

import spacy
from loguru import logger
from spacy.gold import biluo_tags_from_offsets, offsets_from_biluo_tags
from tqdm import tqdm

from deidentify.base import Annotation, Document
from deidentify.tokenizer import Tokenizer

Token = namedtuple('Token', ['text', 'pos_tag', 'label', 'ner_tag'])
ParsedDoc = namedtuple('ParsedDoc', ['spacy_doc', 'name', 'text'])


def standoff_to_sents(docs: List[Document],
                      tokenizer: Tokenizer,
                      verbose=False) -> Tuple[List[List[Token]], List[ParsedDoc]]:
    """Convert corpus into list of BIO tagged sentences.

    Each document is parsed using the spaCy tokenizer and segmented into sentences. Afterwards, each
    sentence is represented as a list of BIO tagged tokens.

    Parameters
    ----------
    docs : List[Document]
        The corpus documents.
    tokenizer : Tokenizer
        A tokenizer instance that parsed the documents using spaCy.

    Returns
    -------
    sents : List[List[Token]]
        List of sentences, where each sentence is a list of BIO tagged tokens.
    sents_docs : List[ParsedDoc]
        The parsed documents where the sentence originates from.
    """
    sents = []
    sents_docs = []

    for doc in tqdm(docs, disable=not verbose, desc='Tokenize documents'):
        parsed_doc = tokenizer.parse_text(doc.text)

        bio_tags = _doc_to_bio(parsed_doc, doc.annotations)

        for sent in parsed_doc.sents:
            sent_tokens = [Token(text=token.text,
                                 pos_tag=token.pos_,
                                 label=bio_tags[token.i],
                                 ner_tag=token.ent_type_)
                           for token in sent]

            # merge sentences where entities cross sentence boundaries
            if sent_tokens[0].label.startswith('I-') or sent_tokens[0].label.startswith('L-'):
                sents[-1].extend(sent_tokens)
            else:
                sents.append(sent_tokens)
                sents_docs.append(ParsedDoc(spacy_doc=parsed_doc, name=doc.name, text=doc.text))

    _validate_labels(sents_docs, sents)
    return sents, sents_docs


def sents_to_standoff(sentence_tags: List[List[str]], docs: List[ParsedDoc]) -> List[Document]:
    """Convert a BIO tagged documents to standoff annotated documents.

    Parameters
    ----------
    sentence_tags : List[List[str]]
        List of sentences of BIO tagged tokens.
    docs : List[ParsedDoc]
        The documents corresponding to each sentence.

    Returns
    -------
    annotated_docs : List[Document]
        The documents with annotated entities in standoff format.

    """
    tags_by_doc = _group_sentences(sentence_tags, docs)

    annotated_docs = []
    for doc, tags in tags_by_doc:
        try:
            annotated_docs.append(Document(
                name=doc.name,
                text=doc.text,
                annotations=_bio_to_standoff(tags, doc.spacy_doc)
            ))
        except Exception as e:
            logger.warning('Could not convert document to standoff {}\n tags = {}\n{}'
                           .format(doc.name, tags, e))

            annotated_docs.append(Document(
                name=doc.name,
                text=doc.text,
                annotations=[]
            ))

    return annotated_docs


def _group_sentences(sentence_tags: List[List[str]],
                     docs: List[ParsedDoc]) -> List[Tuple[ParsedDoc, List[str]]]:
    """Group BIO tagged sentences by document (i.e., merge list of sentences to a single list per
    document).

    This function is used to convert sentence level BIO annotations to standoff format.

    Example:
    ```
    sentence_tags = [['B', 'I', 'O'], ['O', 'O'], ['O', 'O']]
    docs = [d1, d1, d2]

    _group_sentences(sentence_tags, docs)
    -> [['B', 'I', 'O', 'O', 'O'], ['O', 'O']]
    -> [d1, d2]
    ```

    Parameters
    ----------
    sentence_tags : List[List[str]]
        List of sentences. Each sentence contains a list of BIO tags.
    docs : List[ParsedDoc]
        List of documents corresponding to the sentences.

    Returns
    -------
    grouped_sentences : List[Tuple(ParsedDoc, List[str])]
        The sentences grouped by document.

    """
    grouped = defaultdict(list)
    for doc, sentence in zip(docs, sentence_tags):
        grouped[doc].extend(sentence)

    return list(zip(grouped.keys(), grouped.values()))


def _end_of_chunk(next_tag: str) -> bool:
    return not next_tag or next_tag.startswith('O') or next_tag.startswith('B')


def _bio_to_biluo(bio_tags: List[str]) -> List[str]:
    """Convert sentece-level BIO tagging to BILUO.
    """
    biluo_tags = []
    for i in range(len(bio_tags)):

        current_tag = bio_tags[i]
        if i + 1 < len(bio_tags):
            next_tag = bio_tags[i + 1]
        else:
            next_tag = None

        if current_tag.startswith('B-') and _end_of_chunk(next_tag):
            biluo_tags.append('U-' + current_tag[2:])
        elif current_tag.startswith('I-') and _end_of_chunk(next_tag):
            biluo_tags.append('L-' + current_tag[2:])
        else:
            biluo_tags.append(current_tag)

    return biluo_tags


def _bio_to_standoff(bio_tags: List[str], spacy_doc: spacy.tokens.Doc) -> List[Annotation]:
    """Convert BIO tagged document to annotations in standoff format.

    The original spaCy document is used to recreate correct entity offsets.

    Parameters
    ----------
    bio_tags : List[str]
        A BIO tagged sentence. `len(bio_tags) == len(spacy_doc)` has to hold.
    spacy_doc : spacy.tokens.Doc
        The spaCy doc corresponding to the BIO tags.

    Returns
    -------
    List[Annotation]
        The standoff annotations.

    """
    bio_tags = fix_dangling_entities(bio_tags)
    biluo_tags = _bio_to_biluo(bio_tags)
    offsets = offsets_from_biluo_tags(spacy_doc, biluo_tags)

    annotations = []
    for i, offset in enumerate(offsets):
        annotations.append(Annotation(
            text=spacy_doc.char_span(offset[0], offset[1]).text,
            start=offset[0],
            end=offset[1],
            tag=offset[2],
            ann_id='T{}'.format(i),
        ))

    return annotations


def _doc_to_bio(parsed_doc: spacy.tokens.Doc, annotations: List[Annotation]):
    entities = [(int(ann.start), int(ann.end), ann.tag) for ann in annotations]
    biluo_tags = biluo_tags_from_offsets(parsed_doc, entities)

    biluo_to_bio = {
        'B-': 'B-',
        'I-': 'I-',
        'L-': 'I-',
        'U-': 'B-',
    }

    tags = []
    for tag in biluo_tags:
        if tag == "O":
            tags.append('O')
        elif tag == '-':
            # Returned by spacy if token boundaries mismatch entity boundaries.
            # https://spacy.io/api/goldparse#biluo_tags_from_offsets
            tags.append('O')
        else:
            tags.append(biluo_to_bio[tag[0:2]] + tag[2:])

    return tags


def _validate_labels(docs: List[ParsedDoc], sents: List[List[Token]]):
    """Perform sanity checks on BIO tagged sentences.

    * A sentence has to start with either a 'B' or 'O' token.
    * If a token is within an entity (i.e., tagged as 'I'), the preceeding token has to be tagged
    as 'I' or 'B'.

    """
    for doc, sent in zip(docs, sents):
        try:
            assert sent[0].label == 'O' or sent[0].label.startswith('B-')
            for i, token in enumerate(sent[1:]):
                if token.label.startswith('I-'):
                    assert sent[i].label.startswith('B-') or sent[i].label.startswith('I-')
        except:
            logger.warning('Invalid tagging {}, sent={}'.format(doc.name, sent))


def _inside_entity(previous_tag, current_tag):
    return previous_tag != 'O' and previous_tag[2:] == current_tag[2:]


def fix_dangling_entities(tags: List[str]) -> List[str]:
    prev_tag = '<OOB>'
    result = []

    for tag in tags:
        if tag.startswith('I-') and not _inside_entity(prev_tag, tag):
            result.append('B-' + tag[2:])
        else:
            result.append(tag)
        prev_tag = tag

    return result
