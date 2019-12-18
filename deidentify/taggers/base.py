from abc import ABC, abstractmethod
from os.path import isfile
from pathlib import Path
from typing import List

from deidentify.base import Document

cache_root = Path(Path.home(), ".deidentify")


def cached_model_file(model: str) -> Path:
    """Converts a model name to the actual model file (.pickle/.pt) in the model download cache.

    Parameters
    ----------
    model : str
        The model name.

    Returns
    -------
    Path
        The path to the pickle/pt file corresponding to the model name.
    """
    model_path = None

    if model.startswith('model_bilstmcrf_'):
        model_path = Path(cache_root, model, 'final-model.pt')

    if model.startswith('model_crf_'):
        model_path = Path(cache_root, model, 'model.pickle')

    try:
        assert isfile(model_path)
    except AssertionError:
        raise ValueError(
            f'The model "{model}" could not be found in the model cache at "{cache_root}". '
            'You may have to download it first.'
        )

    return model_path


class TextTagger(ABC):

    @abstractmethod
    def annotate(self, documents: List[Document]) -> List[Document]:
        pass

    @property
    @abstractmethod
    def tags(self) -> List[str]:
        pass
