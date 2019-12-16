#!/bin/bash
CORPUS=ons # (ons|i2b2|nursing)

source activate deidentify

# Disable MKL multithreading as it will actually slow down spaCy tokenization
export MKL_NUM_TRHEADS=1
# Specify GPU to run on
export CUDA_VISIBLE_DEVICES=0

# Fraction of training data to use
train_sizes=(0.1 0.25 0.4 0.55 0.7 0.85 1)
# Random seeds for sampling the training data. The number of seeds corresponds to the number of
# repetitions for each training size.
seeds=(42 43 44)

for size in "${train_sizes[@]}"; do
    for seed in "${seeds[@]}"; do
        echo "========= size: $size - seed: $seed ========="

        python deidentify/methods/crf/run_crf_training_sample.py "$CORPUS" subset_training liu_2015 --train_sample_frac="$size" --random_seed="$seed"
        python deidentify/methods/bilstmcrf/run_bilstmcrf_training_sample.py ons subset_training --train_sample_frac="$size" --random_seed="$seed"
    done
done
