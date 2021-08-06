# Train and Evaluate Models

In this guide, we show how to train and evaluate your own models. We assume that you created a corpus with the appropriate [data format](01_data_format.md) in `data/corpus/<corpus_name>`.

## Model Training Scripts

All training scripts are located under `deidentify/methods/` and are prefixed with `run_`. For example, use `deidentify/methods/bilstmcrf/run_bilstmcrf.py` to train a BiLSTM-CRF model.

Each script takes a set of arguments that you can print as follows:

```sh
python deidentify/methods/bilstmcrf/run_bilstmcrf.py --help
```

Below is a list of available scripts:

```sh
> tree -P run_*.py -I __* deidentify/methods/
deidentify/methods/
├── bilstmcrf
│   ├── run_bilstmcrf.py                    # Train a BiLSTM-CRF
│   └── run_bilstmcrf_training_sample.py    # Train a BiLSTM-CRF with a fraction of the training set
├── crf
│   ├── run_crf.py                          # Train a CRF model
│   ├── run_crf_hyperopt.py                 # Perform a random search for a CRF model
│   ├── run_crf_learning_curve.py           # Print a learning curve for a CRF model
│   └── run_crf_training_sample.py          # Train a CRF with a fraction of the training set
└── deduce
    └── run_deduce.py                       # Run the DEDUCE tagger on your dataset
```

All scripts save their predictions and model artifacts (e.g., pickle files, training logs) to `output/predictions/<corpus_name>/<script>_<run_id>/`. This allows you to evaluate the predictions at a later stage.

## Example: Train and Evaluate a BiLSTM-CRF Model

Execute the command below to run the BiLSTM-CRF pipeline on the corpus `ons` (aka. NUT) with run id `demo_run`:

```sh
python deidentify/methods/bilstmcrf/run_bilstmcrf.py ons demo_run \
    --pooled_contextual_embeddings \
    --train_with_dev
```

The script saves the train/dev/test set predictions to `output/predictions/ons/bilstmcrf_dummy_run`. We can the script below to evaluate a single run:

```sh
python deidentify/evaluation/evaluate_run.py nl data/corpus/ons/test/ data/corpus/ons/test/ output/predictions/ons/bilstmcrf_demo_run/test/
```

It should print an evaluation report on an entity-level, token-level and blind token-level for each PHI tag. Example:

```
> python deidentify/evaluation/evaluate_run.py nl data/corpus/ons/test/ data/corpus/ons/test/ output/predictions/ons/bilstmcrf_demo_run/test/

entity level        	tp: 3168  - fp: 288   - fn: 469   - tn: 0     - precision: 0.9167 - recall: 0.8710 - accuracy: 0.8071 - f1-score: 0.8933
Address             	tp: 132   - fp: 26    - fn: 24    - tn: 0     - precision: 0.8354 - recall: 0.8462 - accuracy: 0.7253 - f1-score: 0.8408
Age                 	tp: 30    - fp: 8     - fn: 11    - tn: 0     - precision: 0.7895 - recall: 0.7317 - accuracy: 0.6122 - f1-score: 0.7595
Care_Institute      	tp: 142   - fp: 65    - fn: 74    - tn: 0     - precision: 0.6860 - recall: 0.6574 - accuracy: 0.5053 - f1-score: 0.6714
Date                	tp: 739   - fp: 59    - fn: 64    - tn: 0     - precision: 0.9261 - recall: 0.9203 - accuracy: 0.8573 - f1-score: 0.9232
Email               	tp: 10    - fp: 1     - fn: 0     - tn: 0     - precision: 0.9091 - recall: 1.0000 - accuracy: 0.9091 - f1-score: 0.9524
Hospital            	tp: 7     - fp: 2     - fn: 3     - tn: 0     - precision: 0.7778 - recall: 0.7000 - accuracy: 0.5833 - f1-score: 0.7369
ID                  	tp: 12    - fp: 3     - fn: 13    - tn: 0     - precision: 0.8000 - recall: 0.4800 - accuracy: 0.4286 - f1-score: 0.6000
Initials            	tp: 111   - fp: 23    - fn: 67    - tn: 0     - precision: 0.8284 - recall: 0.6236 - accuracy: 0.5522 - f1-score: 0.7116
Internal_Location   	tp: 28    - fp: 10    - fn: 27    - tn: 0     - precision: 0.7368 - recall: 0.5091 - accuracy: 0.4308 - f1-score: 0.6021
Name                	tp: 1856  - fp: 67    - fn: 85    - tn: 0     - precision: 0.9652 - recall: 0.9562 - accuracy: 0.9243 - f1-score: 0.9607
Organization_Company	tp: 71    - fp: 20    - fn: 65    - tn: 0     - precision: 0.7802 - recall: 0.5221 - accuracy: 0.4551 - f1-score: 0.6256
Other               	tp: 0     - fp: 0     - fn: 4     - tn: 0     - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
Phone_fax           	tp: 16    - fp: 2     - fn: 0     - tn: 0     - precision: 0.8889 - recall: 1.0000 - accuracy: 0.8889 - f1-score: 0.9412
Profession          	tp: 11    - fp: 1     - fn: 31    - tn: 0     - precision: 0.9167 - recall: 0.2619 - accuracy: 0.2558 - f1-score: 0.4074
SSN                 	tp: 0     - fp: 1     - fn: 0     - tn: 0     - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
URL_IP              	tp: 3     - fp: 0     - fn: 1     - tn: 0     - precision: 1.0000 - recall: 0.7500 - accuracy: 0.7500 - f1-score: 0.8571

token level         	tp: 4894  - fp: 308   - fn: 500   - tn: 1810993 - precision: 0.9408 - recall: 0.9073 - accuracy: 0.8583 - f1-score: 0.9237
Address             	tp: 217   - fp: 22    - fn: 29    - tn: 120845 - precision: 0.9079 - recall: 0.8821 - accuracy: 0.8097 - f1-score: 0.8948
Age                 	tp: 48    - fp: 11    - fn: 13    - tn: 121041 - precision: 0.8136 - recall: 0.7869 - accuracy: 0.6667 - f1-score: 0.8000
Care_Institute      	tp: 266   - fp: 78    - fn: 81    - tn: 120688 - precision: 0.7733 - recall: 0.7666 - accuracy: 0.6259 - f1-score: 0.7699
Date                	tp: 1835  - fp: 66    - fn: 36    - tn: 119176 - precision: 0.9653 - recall: 0.9808 - accuracy: 0.9473 - f1-score: 0.9730
Email               	tp: 10    - fp: 1     - fn: 0     - tn: 121102 - precision: 0.9091 - recall: 1.0000 - accuracy: 0.9091 - f1-score: 0.9524
Hospital            	tp: 11    - fp: 3     - fn: 3     - tn: 121096 - precision: 0.7857 - recall: 0.7857 - accuracy: 0.6471 - f1-score: 0.7857
ID                  	tp: 12    - fp: 3     - fn: 12    - tn: 121086 - precision: 0.8000 - recall: 0.5000 - accuracy: 0.4444 - f1-score: 0.6154
Initials            	tp: 113   - fp: 21    - fn: 72    - tn: 120907 - precision: 0.8433 - recall: 0.6108 - accuracy: 0.5485 - f1-score: 0.7085
Internal_Location   	tp: 47    - fp: 11    - fn: 45    - tn: 121010 - precision: 0.8103 - recall: 0.5109 - accuracy: 0.4563 - f1-score: 0.6267
Name                	tp: 2135  - fp: 60    - fn: 80    - tn: 118838 - precision: 0.9727 - recall: 0.9639 - accuracy: 0.9385 - f1-score: 0.9683
Organization_Company	tp: 119   - fp: 27    - fn: 89    - tn: 120878 - precision: 0.8151 - recall: 0.5721 - accuracy: 0.5064 - f1-score: 0.6723
Other               	tp: 0     - fp: 0     - fn: 5     - tn: 121108 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
Phone_fax           	tp: 38    - fp: 2     - fn: 0     - tn: 121073 - precision: 0.9500 - recall: 1.0000 - accuracy: 0.9500 - f1-score: 0.9744
Profession          	tp: 40    - fp: 3     - fn: 34    - tn: 121036 - precision: 0.9302 - recall: 0.5405 - accuracy: 0.5195 - f1-score: 0.6837
URL_IP              	tp: 3     - fp: 0     - fn: 1     - tn: 121109 - precision: 1.0000 - recall: 0.7500 - accuracy: 0.7500 - f1-score: 0.8571

token (blind)       	tp: 5016  - fp: 187   - fn: 379   - tn: 115532 - precision: 0.9641 - recall: 0.9297 - accuracy: 0.8986 - f1-score: 0.9466
ENT                 	tp: 5016  - fp: 187   - fn: 379   - tn: 115532 - precision: 0.9641 - recall: 0.9297 - accuracy: 0.8986 - f1-score: 0.9466
```

You can use the `evaluate_corpus.py` script to evaluate all runs for a given corpus. The script produces a CSV file with the evaluation measures for each corpus part (i.e., train/dev/test) that you can use this for further analysis.

```sh
> python deidentify/evaluation/evaluate_corpus.py <corpus_name> <language>
[...]
> tree output/evaluation/<corpus_name>
output/evaluation/<corpus_name>
├── summary_dev.csv
├── summary_test.csv
└── summary_train.csv
```
