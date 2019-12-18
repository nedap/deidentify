# Corpus Format

This guide explains how you can convert your own annotated data to the corpus format used in this project. You can then use that corpus to train your own sequence labeling models.

## Data Format

We use the [brat standoff annotation format](https://brat.nlplab.org/standoff.html). You will need two files for each document in your dataset: `document_[id].txt` and `document_[id].ann`.

Example `document_1.txt`:

```
Dit is stukje tekst met daarin de naam Ilker Koopal. De patient I. Koopal (e: b.bctzl@sujko.com, t: 06-16769063) is 64 jaar oud
en woonachtig in Orvelte. Hij werd op 22 november door arts Omid Esajas ontslagen van de kliniek van het UMCU.
```

Example `document_1.ann`:

```
T1 Name 39 51 Ilker Koopal
T2 Name 64 73 I. Koopal
T3 Email 78 95 b.bctzl@sujko.com
T4 Phone_fax 100 111 06-16769063
T5 Age 116 123 64 jaar
T6 Address 145 152 Orvelte
T7 Date 166 177 22 november
T8 Name 188 199 Omid Esajas
T9 Hospital 233 237 UMCU
```

## Corpus Location

After you converted your documents to the standoff format, copy them to the `data/corpus/<corpus_name>/` directory. Here is an example for the `dummy` corpus. In all experiment code, we follow the convention that the name of corpus directory identifies the dataset.

```
data/
└── corpus
    └── dummy
        ├── dev
        │   ├── example-3.ann
        │   └── example-3.txt
        ├── test
        │   ├── example-2.ann
        │   └── example-2.txt
        └── train
            ├── example-1.ann
            └── example-1.txt
```

### Create a train/dev/test Split

If you don't have a predefined train/dev/test split, you can also use the following utility to create one:

```
python deidentify/dataset/brat2corpus.py <corpus_name> <data_path>
```

This script will take all `*.ann/*.txt` in `data_path` and create a new corpus at `data/corpus/<corpus_name>` with a 60/20/20 train/dev/test set ratio.

### Load Your Corpus

After you created your corpus at `data/corpus/<corpus_name>` you should be able to load it by executing:

```py
from deidentify.dataset.corpus_loader import CorpusLoader, CORPUS_PATH

# Pick the name of your corpus here:
corpus = CorpusLoader().load_corpus(path=CORPUS_PATH['dummy'])
print(corpus)

# This should print:
# Corpus(name=dummy). Number of Documents (train/dev/test): 1/1/1
```
