# deidentify

A Python library to de-identify medical records with state-of-the-art NLP methods. Pre-trained models for the Dutch language are available.

## Quick Start

### Installation

Create a new virtual environment with an environment manager of your choice. Then, install `deidentify`:

```sh
pip install deidentify
```

### Example Usage

Below, we will create an example document and run a pre-trained de-identification model over it. First, let's download a pre-trained model and save it in the model cache at `~/.deidentify`. See below for a [list of available models](#pre-trained-models).

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

There are currently three taggers that you can use:

   * `deidentify.taggers.DeduceTagger`: A wrapper around the DEDUCE tagger by Menger et al. (2018, [code](https://github.com/vmenger/deduce), [paper](https://www.sciencedirect.com/science/article/abs/pii/S0736585316307365))
   * `deidentify.taggers.CRFTagger`: A CRF tagger using the feature set by Liu et al. (2015, [paper](https://www.sciencedirect.com/science/article/pii/S1532046415001197))
   * `deidentify.taggers.FlairTagger`: A wrapper around the Flair [`SequenceTagger`](https://github.com/zalandoresearch/flair/blob/2d6e89bdfe05644b4e5c7e8327f6ecc6b834ec9e/flair/models/sequence_tagger_model.py#L68) allowing the use of neural architectures such as BiLSTM-CRF. The pre-trained models below use contextualized string embeddings by Akbik et al. (2018, [paper](https://www.aclweb.org/anthology/C18-1139/))

All taggers implement the `deidentify.taggers.TextTagger` interface which you can implement to provide your own taggers.

## Pre-trained Models

We provide a number of pre-trained models for the Dutch language. The models were developed on the Nedap/University of Twente (NUT) dataset. The dataset consists of 1260 documents from three domains of Dutch healthcare: elderly care, mental care and disabled care (note: in the codebase we sometimes also refer to this dataset as `ons`). More information on the design of the dataset can be found in [our paper](TODO).


| Name | Tagger | Language | Dataset | F1* | Precision* | Recall* | Tags |
|------|--------|----------|---------|----|-----------|--------|--------|
| [DEDUCE (Menger et al., 2018)](https://www.sciencedirect.com/science/article/abs/pii/S0736585316307365)** | `DeduceTagger` | Dutch | NUT | 0.7564 | 0.9092 | 0.6476 | [8 PHI Tags](https://github.com/nedap/deidentify/blob/168ad67aec586263250900faaf5a756d3b8dd6fa/deidentify/methods/deduce/run_deduce.py#L17) |
| [model_crf_ons_tuned-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_crf_ons_tuned-v0.1.0) | `CRFTagger` | Dutch | NUT | 0.9048 | 0.9632 | 0.8530 | [15 PHI Tags](https://github.com/nedap/deidentify/releases/tag/model_crf_ons_tuned-v0.1.0) |
| [model_bilstmcrf_ons_fast-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_fast-v0.1.0) | `FlairTagger`  | Dutch | NUT | 0.9461 | 0.9591 | 0.9335 | [15 PHI Tags](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_fast-v0.1.0) |
| [model_bilstmcrf_ons_large-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_large-v0.1.0) | `FlairTagger` | Dutch | NUT | 0.9505 | 0.9683 | 0.9333 | [15 PHI Tags](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_large-v0.1.0) |

*\*All scores are micro-averaged, blind token-level precision/recall/F1 obtained on the test portion of each dataset. For additional metrics, see the corresponding model release.*

*\*DEDUCE was developed on a dataset of psychiatric nurse notes and treatment plans. The numbers reported here were obtained by applying DEDUCE to our NUT dataset. For more information on the development of DEDUCE, see the paper by [Menger et al. (2018)](https://www.sciencedirect.com/science/article/abs/pii/S0736585316307365).*

## Package Development

If you want to make changes to the source of the package or run your own experiments, you can use the following environment:

```sh
# Install package dependencies and add local files to PYTHONPATH of that environment.
conda env create -f environment.yml
conda activate deidentify && export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Add test dependencies
pip install pytest pytest-cov pylint
```

To run unit tests and code linting, execute:

```sh
make test

make lint
```

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
