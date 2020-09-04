# deidentify

A Python library to de-identify medical records with state-of-the-art NLP methods. Pre-trained models for the Dutch language are available.

This repository shares the resources developed in the following paper:

> J. Trienes, D. Trieschnigg, C. Seifert, and D. Hiemstra. Comparing Rule-based, Feature-based and Deep Neural Methods for De-identification of Dutch Medical Records. In: *Proceedings of the 1st ACM WSDM Health Search and Data Mining Workshop (HSDM)*, 2020.

You can get the authors' version of the paper from this link: [paper](https://arxiv.org/abs/2001.05714).

Blog post: https://medium.com/nedap/de-identification-of-ehr-using-nlp-a270d40fc442.

## Quick Start

### Installation

Create a new virtual environment with an environment manager of your choice. Then, install `deidentify`:

```sh
pip install deidentify
```

We use the spaCy tokenizer. For good compatibility with the pre-trained models, we recommend using the same spaCy tokenization models that were used at de-identification model training time:

```sh
pip install https://github.com/explosion/spacy-models/releases/download/nl_core_news_sm-2.2.1/nl_core_news_sm-2.2.1.tar.gz#egg=nl_core_news_sm==2.2.1
```

### Example Usage

Below, we will create an example document and run a pre-trained de-identification model over it. First, let's download a pre-trained model and save it in the model cache at `~/.deidentify`. See below for a [list of available models](#pre-trained-models).

```sh
python -m deidentify.util.download_model model_bilstmcrf_ons_fast-v0.1.0
```

Then, we can create a document, load the tagger with the pre-trained model, and finally annotate the document.

```py
from deidentify.base import Document
from deidentify.taggers import FlairTagger
from deidentify.tokenizer import TokenizerFactory

# Create some text
text = (
    "Dit is stukje tekst met daarin de naam Jan Jansen. De patient J. Jansen (e: "
    "j.jnsen@email.com, t: 06-12345678) is 64 jaar oud en woonachtig in Utrecht. Hij werd op 10 "
    "oktober door arts Peter de Visser ontslagen van de kliniek van het UMCU."
)

# Wrap text in document
documents = [
    Document(name='doc_01', text=text)
]

# Select downloaded model
model = 'model_bilstmcrf_ons_fast-v0.1.0'

# Instantiate tokenizer
tokenizer = TokenizerFactory().tokenizer(corpus='ons', disable=("tagger", "ner"))

# Load tagger with a downloaded model file and tokenizer
tagger = FlairTagger(model=model, tokenizer=tokenizer, verbose=False)

# Annotate your documents
annotated_docs = tagger.annotate(documents)
```

This completes the annotation stage. Let's inspect the entities that the tagger found:

```py
from pprint import pprint

first_doc = annotated_docs[0]
pprint(first_doc.annotations)
```

This should print the entities of the first document.

```py
[Annotation(text='Jan Jansen', start=39, end=49, tag='Name', doc_id='', ann_id='T0'),
 Annotation(text='J. Jansen', start=62, end=71, tag='Name', doc_id='', ann_id='T1'),
 Annotation(text='j.jnsen@email.com', start=76, end=93, tag='Email', doc_id='', ann_id='T2'),
 Annotation(text='06-12345678', start=98, end=109, tag='Phone_fax', doc_id='', ann_id='T3'),
 Annotation(text='64 jaar', start=114, end=121, tag='Age', doc_id='', ann_id='T4'),
 Annotation(text='Utrecht', start=143, end=150, tag='Address', doc_id='', ann_id='T5'),
 Annotation(text='10 oktober', start=164, end=174, tag='Date', doc_id='', ann_id='T6'),
 Annotation(text='Peter de Visser', start=185, end=200, tag='Name', doc_id='', ann_id='T7'),
 Annotation(text='UMCU', start=234, end=238, tag='Hospital', doc_id='', ann_id='T8')]
```

#### Masking or Replacing Annotations

Often, it is desirable to remove the sensitive annotations from the documents. `deidentify` implements two strategies:

1. **Masking:** replace annotations with placeholders. Example: `Jan Jansen -> [Name]`
1. **Surrogates [experimental]:** replace annotations with random but realistic alternatives. Example: `Jan Jansen -> Bart Bakker`. The surrogate replacement strategy follows [Stubbs et al. (2015)](https://doi.org/10.1007/978-3-319-23633-9_27).

##### Masking
Continuing from the example above, this is how to mask annotations:

```py
from deidentify.util import mask_annotations

masked_doc = mask_annotations(first_doc)
print(masked_doc.text)
```

Which should print:

> Dit is stukje tekst met daarin de naam [NAME]. De patient [NAME] (e: [EMAIL], t: [PHONE_FAX]) is [AGE] oud en woonachtig in [ADDRESS]. Hij werd op [DATE] door arts [NAME] ontslagen van de kliniek van het [HOSPITAL].

##### Surrogates [experimental]

And this is how to generate surrogates:

```py
from deidentify.util import surrogate_annotations

# The surrogate generation process involves some randomness.
# You can set a seed to make the process deterministic.
iter_docs = surrogate_annotations(docs=[first_doc], seed=1)
surrogate_doc = list(iter_docs)[0]
print(surrogate_doc.text)
```

This code should print:

> Dit is stukje tekst met daarin de naam Gijs Hermelink. De patient G. Hermelink (e: n.qvgjj@spqms.com, t: 06-83662585) is 64 jaar oud en woonachtig in Cothen. Hij werd op 28 juni door arts Jullian van Troost ontslagen van de kliniek van het UMCU.

### Available Taggers

There are currently three taggers that you can use:

   * `deidentify.taggers.DeduceTagger`: A wrapper around the DEDUCE tagger by Menger et al. (2018, [code](https://github.com/vmenger/deduce), [paper](https://www.sciencedirect.com/science/article/abs/pii/S0736585316307365))
   * `deidentify.taggers.CRFTagger`: A CRF tagger using the feature set by Liu et al. (2015, [paper](https://www.sciencedirect.com/science/article/pii/S1532046415001197))
   * `deidentify.taggers.FlairTagger`: A wrapper around the Flair [`SequenceTagger`](https://github.com/zalandoresearch/flair/blob/2d6e89bdfe05644b4e5c7e8327f6ecc6b834ec9e/flair/models/sequence_tagger_model.py#L68) allowing the use of neural architectures such as BiLSTM-CRF. The pre-trained models below use contextualized string embeddings by Akbik et al. (2018, [paper](https://www.aclweb.org/anthology/C18-1139/))

All taggers implement the `deidentify.taggers.TextTagger` interface which you can implement to provide your own taggers.

### Tag Set

A `deidentify.taggers.TextTagger` has a `tags` property that can be used to get the supported tags. Example: the FlairTagger tagger in above demo has following tags:

```py
>>> tagger.tags
['Internal_Location', 'Age', 'Phone_fax', 'Name', 'SSN', 'Hospital', 'Email', 'Initials', 'O',
'Organization_Company', 'ID', 'Profession', 'Care_Institute', 'Other', 'Date', 'URL_IP', 'Address']
```

### Pre-trained Models

We provide a number of pre-trained models for the Dutch language. The models were developed on the Nedap/University of Twente (NUT) dataset. The dataset consists of 1260 documents from three domains of Dutch healthcare: elderly care, mental care and disabled care (note: in the codebase we sometimes also refer to this dataset as `ons`). More information on the design of the dataset can be found in [our paper](https://arxiv.org/abs/2001.05714).


| Name | Tagger | Language | Dataset | F1* | Precision* | Recall* | Tags |
|------|--------|----------|---------|----|-----------|--------|--------|
| [DEDUCE (Menger et al., 2018)](https://www.sciencedirect.com/science/article/abs/pii/S0736585316307365)** | `DeduceTagger` | Dutch | NUT | 0.7564 | 0.9092 | 0.6476 | [8 PHI Tags](https://github.com/nedap/deidentify/blob/168ad67aec586263250900faaf5a756d3b8dd6fa/deidentify/methods/deduce/run_deduce.py#L17) |
| [model_crf_ons_tuned-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_crf_ons_tuned-v0.1.0) | `CRFTagger` | Dutch | NUT | 0.9048 | 0.9632 | 0.8530 | [15 PHI Tags](https://github.com/nedap/deidentify/releases/tag/model_crf_ons_tuned-v0.1.0) |
| [model_bilstmcrf_ons_fast-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_fast-v0.1.0) | `FlairTagger`  | Dutch | NUT | 0.9461 | 0.9591 | 0.9335 | [15 PHI Tags](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_fast-v0.1.0) |
| [model_bilstmcrf_ons_large-v0.1.0](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_large-v0.1.0) | `FlairTagger` | Dutch | NUT | 0.9505 | 0.9683 | 0.9333 | [15 PHI Tags](https://github.com/nedap/deidentify/releases/tag/model_bilstmcrf_ons_large-v0.1.0) |

*\*All scores are micro-averaged, blind token-level precision/recall/F1 obtained on the test portion of each dataset. For additional metrics, see the corresponding model release.*

*\*\*DEDUCE was developed on a dataset of psychiatric nursing notes and treatment plans. The numbers reported here were obtained by applying DEDUCE to our NUT dataset. For more information on the development of DEDUCE, see the paper by [Menger et al. (2018)](https://www.sciencedirect.com/science/article/abs/pii/S0736585316307365).*

## Running Experiments and Training Models

If you have your own dataset of annotated documents and you want to train your own models on it, you can take a look at the following guides:

   * [Convert your data into our corpus format](docs/01_data_format.md)
   * [Train and evaluate your own models](docs/02_train_evaluate_models.md)
   * [Logging and pipeline verbosity](docs/06_pipeline_verbosity.md)

If you want more information on the experiments in our paper, have a look here:

   * [NUT annotation guidelines](docs/03_hsdm2020_nut_annotation_guidelines.md)
   * [Surrogate generation procedure](docs/04_hsdm2020_surrogate_generation.md)
   * [Experiments on English corpora: i2b2/UTHealth and nursing notes](docs/05_hsdm2020_english_datasets.md)

### Computational Environment

When you want to run your own experiments, we assume that you clone this code base locally and execute all scripts under `deidentify/` within the following conda environment:

```sh
# Install package dependencies and add local files to the Python path of that environment.
conda env create -f environment.yml
conda activate deidentify && export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Citation

Please cite the following paper when using `deidentify`:

```bibtex
@inproceedings{Trienes:2020:CRF,
  title={Comparing Rule-based, Feature-based and Deep Neural Methods for De-identification of Dutch Medical Records},
  author={Trienes, Jan and Trieschnigg, Dolf and Seifert, Christin and Hiemstra, Djoerd},
  booktitle = {Proceedings of the 1st ACM WSDM Health Search and Data Mining Workshop},
  series = {{HSDM} 2020},
  year = {2020}
}
```

## Contact

If you have any question, please contact Jan Trienes at jan.trienes@nedap.com.
