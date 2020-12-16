from abc import ABC, abstractmethod
from os.path import isfile
from pathlib import Path
from typing import List

from loguru import logger

import deidentify
from deidentify.base import Document
from deidentify.util import download_model
import tarfile


def lookup_model(model):
    """Get model file from model name. If `model` is a path to an existing file on the file system,
    `model` is returned instead. Otherwise, this function searches for a model in the model download
    cache.
    """
    if isfile(model):
        return model

    return cached_model_file(model)


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
    model_path = Path(model)

    if model.startswith('model_bilstmcrf_'):
        model_path = Path(deidentify.cache_root, model, 'final-model.pt')

    if model.startswith('model_crf_'):
        model_path = Path(deidentify.cache_root, model, 'model.pickle')

    try:
        assert isfile(model_path)
    except AssertionError:
        logger.info(
            'The model "{}" could not be found in the model cache "{}". Attempt to download...',
            model,
            deidentify.cache_root
        )

        class DownloadArgs:
            owner = 'nedap'
            repo = 'deidentify'
            tag = model
            cache_dir = deidentify.cache_root

        try:
            download_model.main(DownloadArgs)
            assert isfile(model_path)
        except (tarfile.ReadError, AssertionError) as e:
            raise ValueError('Unexpected error during model download.') from e

    return model_path


class TextTagger(ABC):

    @abstractmethod
    def annotate(self, documents: List[Document]) -> List[Document]:
        pass

    @property
    @abstractmethod
    def tags(self) -> List[str]:
        pass
