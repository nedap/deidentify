from abc import ABC, abstractmethod
from typing import List

from deidentify.base import Document


class TextTagger(ABC):

    @abstractmethod
    def annotate(self, documents: List[Document]) -> List[Document]:
        pass

    @property
    @abstractmethod
    def tags(self) -> List[str]:
        pass
