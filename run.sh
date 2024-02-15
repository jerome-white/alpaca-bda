#!/bin/bash

ROOT=`git rev-parse --show-toplevel`
ALPACA_EVAL=alpaca_eval
ALPACA_GIT=$ROOT/$ALPACA_EVAL

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

if [ -d $ALPACA_GIT ]; then
    (cd $ALPACA_GIT && git pull origin main) 1>&2
else
    git clone https://github.com/tatsu-lab/${ALPACA_EVAL}.git
fi

python compile-results.py --results $ALPACA_GIT/results \
    | python prompt-encoder.py --record prompts.json \
    | python aggregate-data.py \
    | python stan-encoder.py --record models.csv
