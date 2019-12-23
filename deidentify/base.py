from collections import namedtuple
from typing import List


class Annotation(namedtuple('Annotation', ['text', 'start', 'end', 'tag', 'doc_id', 'ann_id'])):
    """A document annotation. This class is immutable and hashable.

    Annotation ID is ignored while comparing for equality.
    """

    __slots__ = ()

    # pylint: disable=too-many-arguments
    def __new__(cls, text, start, end, tag, doc_id='', ann_id=''):
        return super(Annotation, cls).__new__(cls, text, start, end, tag, doc_id, ann_id)

    def __str__(self):
        t = u"Annotation(text='{}', start={}, end={}, tag='{}', doc_id='{}', ann_id='{}')"
        return t.format(self.text, self.start, self.end, self.tag, self.doc_id, self.ann_id)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.text == other.text \
            and self.start == other.start \
            and self.end == other.end \
            and self.tag == other.tag \
            and self.doc_id == other.doc_id

    def __hash__(self):
        return hash((self.text, self.start, self.end, self.tag, self.doc_id))


class Document:

    def __init__(self, name: str, text: str, annotations: List[Annotation] = ()):
        self.name = name
        self.text = text
        self.annotations = annotations

    def __str__(self):
        t = u"Document(name={}). Chars: {}, Annotations: {}"
        return t.format(self.name, len(self.text), len(self.annotations))

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


class Corpus:

    def __init__(self,
                 train: List[Document],
                 test: List[Document],
                 dev: List[Document] = None,
                 name: str = ''):
        self.train = train
        self.test = test
        self.dev = dev
        self.name = name

    def __str__(self):
        t = u"Corpus(name={}). Number of Documents (train/dev/test): {}/{}/{}"
        return t.format(self.name, len(self.train), len(self.dev), len(self.test))

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()
