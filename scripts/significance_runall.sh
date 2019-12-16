#!/bin/bash

source activate deidentify

TRIALS=9999
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python "$DIR"/../deidentify/evaluation/significance_testing.py \
  "$DIR"/config/significance_ons.yaml --trials $TRIALS

python "$DIR"/../deidentify/evaluation/significance_testing.py \
  "$DIR"/config/significance_i2b2.yaml --trials $TRIALS

python "$DIR"/../deidentify/evaluation/significance_testing.py \
  "$DIR"/config/significance_nursing.yaml --trials $TRIALS
