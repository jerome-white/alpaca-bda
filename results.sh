#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

STAN_MODEL=$ROOT/models/bradley-terry

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

python aggregate-output.py --results $STAN_MODEL/output \
    | python calculate-ability.py --models $ROOT/models.csv \
    | python plot-ability.py --best 10 --output ability.png
