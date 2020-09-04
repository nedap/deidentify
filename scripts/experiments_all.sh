#!/bin/bash
# Use this script to execute all experiments for a single corpus
# Evaluation output will be in output/evaluation/<CORPUS>/summary{train,dev,test}.csv

CORPUS=ons # (ons|i2b2|nursing)

source activate deidentify

# Disable MKL multithreading as it will actually slow down spaCy tokenization
export MKL_NUM_TRHEADS=1

# DEDUCE, only if on "ons" corpus
if [ "$CORPUS" == "ons" ]; then
  python deidentify/methods/deduce/run_deduce.py ons-flattened run_1
  python deidentify/methods/deduce/unflatten_deduce_predictions.py ons deduce_run_1
fi

# CRF
python deidentify/methods/crf/run_crf.py "$CORPUS" run_1 liu_2015
python deidentify/methods/crf/run_crf_hyperopt.py "$CORPUS" regularization_rs liu_2015 \
  --n_iter 250 --n_jobs 44

# BiLSTM, should be run on a GPU machine
export CUDA_VISIBLE_DEVICES=0
python deidentify/methods/bilstmcrf/run_bilstmcrf.py "$CORPUS" initial_run \
    --pooled_contextual_embeddings
python deidentify/methods/bilstmcrf/run_bilstmcrf.py "$CORPUS" train_with_dev \
    --train_with_dev --pooled_contextual_embeddings

# Evaluation
python deidentify/evaluation/evaluate_corpus.py "$CORPUS"
