# Benchmark on English Datasets

In [our paper](TODO), we also test the performance of the CRF and BiLSTM-CRF on two English
datasets:

* Nursing notes (https://physionet.org/physiotools/deid/)
* i2b2/UTHealth 2014 (https://www.i2b2.org/NLP/DataSets/)

Both datasets can be obtained after signing a data use agreement with the corresponding research institutes. Below, we show how to convert those datasets to the [standoff format](01_data_format.md) used throughout this project. The datasets are placed in `data/corpus/nursing` and `data/corpus/i2b2`. Afterwards, the datasets can be used to [train and evaluate models](02_train_evaluate_models) on them.

## Nursing Notes

Assuming the `raw-notes.txt` and `id-phi.phrase` files are located in `data/raw/nursing-notes/`, the nursing notes Corpus can be generated as follows:

```sh
# Convert nursing notes corpus to brat format
NN_DATA=data/raw/nursing-notes
python deidentify/dataset/nursing2brat.py \
    $NN_DATA/notes-raw.txt \
    $NN_DATA/id-phi.phrase \
    $NN_DATA/brat/

# Split nursing notes into 60/20/20 train/dev/test set
python deidentify/dataset/brat2corpus.py nursing $NN_DATA/brat
```

## i2b2/UTHealth

The script assumes that `training-PHI-Gold-Set1`, `training-PHI-Gold-Set2`, and `testing-PHI-Gold-fixed` are located in `data/raw/i2b2/`. The corpus can then be generated as follows:

```sh
python deidentify/dataset/uthealth2corpus.py
```
