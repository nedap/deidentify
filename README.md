# deidentify

A Python library to de-identify medical records with state-of-the-art NLP methods. Pre-trained models for the Dutch and English language are available.

## Quick Start

### Installation

Create a new virtual environment with an environment manager of your choice. Then, install `deidentify`:

```sh
pip install deidentify
```

### Example Usage

Below, we will create an example document and run a pre-trained de-identification model over it. First, let's download a pre-trained and save it in the model cache at `~/.deidentify`. See [below](#pre-trained-models) for a list of available models.

```sh
python -m deidentify.util.download_model model_bilstmcrf_ons_fast-v0.1.0 ~/.deidentify
```

Then, we can create a document, load the tagger with the pre-trained model, and finally annotate the document.

```py
from deidentify.base import Annotation, Document
from deidentify.taggers import FlairTagger
from deidentify.tokenizer import TokenizerFactory

# Create a document
documents = [
    Document(name='doc_01', text='Jan Jansen vanuit het UMCU.', annotations=[])
]

# Select downloaded model
model_file='~/.deidentify/model_bilstmcrf_ons_fast-v0.1.0/final-model.pt'

# Instantiate tokenizer
tokenizer = TokenizerFactory().tokenizer(corpus='ons', disable=("tagger", "ner"))

# Load tagger with a downloaded model file and tokenizer
tagger = FlairTagger(
    model_file=model_file,
    tokenizer=tokenizer
)

# Annotate your documents
annotated_docs = tagger.annotate(documents)
```

This completes the annotation stage. Let's inspect the entities that the tagger found:

```py
from pprint import pprint

first_doc_annotations = annotated_docs[0].annotations
pprint(first_doc_annotations)
```

This should print the entities of the first document.

```py
[Annotation(text='Jan Jansen', start='0', end='11', tag='Name', doc_id='', ann_id='T0'),
Annotation(text='UMCU', start='23', end='27', tag='Hospital', doc_id='', ann_id='T1')]
```

Afterwards, you can replace or remove the discovered entities from the documents.

### Available Taggers

## Pre-trained Models

| Name | Tagger | Language | Dataset | F1* | Precision* | Recall* |
|------|--------|----------|---------|----|-----------|--------|
| [DEDUCE (Menger, 2018)](https://www.sciencedirect.com/science/article/abs/pii/S0736585316307365) | `DeduceTagger` | Dutch | NUT | 0.7564 | 0.9092 | 0.6476 |
| [model_crf_ons_tuned-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_crf_ons_tuned-v0.1.0) | `CRFTagger` | Dutch | NUT | 0.9048 | 0.9632 | 0.8530 |
| [model_bilstmcrf_ons_fast-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_fast-v0.1.0) | `FlairTagger`  | Dutch | NUT | 0.9461 | 0.9591 | 0.9335 |
| [model_bilstmcrf_ons_large-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_large-v0.1.0) | `FlairTagger` | Dutch | NUT | 0.9505 | 0.9683 | 0.9333 |

*\*All scores are micro-averaged, blind token-level precision/recall/F1 obtained on the test portion of each dataset.*

## Citation

Please cite the following paper when using `deidentify`:

```bibtex
@inproceedings{Trienes:2020:CRF,
  title={Comparing Rule-based, Feature-based and Deep Neural Methods for De-identification of Dutch Medical Records},
  author={Trienes, Jan and Trieschnigg, Dolf and Seifert, Christin and Hiemstra, Djoerd},
  booktitle = {Proceedings of the 1st Health Search and Data Mining Workshop},
  series = {{HSDM} 2020},
  year = {2020}
}
```
