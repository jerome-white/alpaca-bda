#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

STAN_MODEL=$ROOT/models/bradley-terry

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

python aggregate-output.py --results $STAN_MODEL/output \
    | python add-model-names.py --models $ROOT/models.csv --chunk-size 100000
