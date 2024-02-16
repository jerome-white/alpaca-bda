#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

ALPACA_EVAL=alpaca_eval
ALPACA_GIT=$ROOT/$ALPACA_EVAL
STAN_MODEL=$ROOT/models/bradley-terry

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

if [ -d $ALPACA_GIT ]; then
    (cd $ALPACA_GIT && git pull origin main) 1>&2
else
    git clone https://github.com/tatsu-lab/${ALPACA_EVAL}.git
fi

python compile-results.py --results $ALPACA_GIT/results \
    | python prompt-encoder.py --record prompts.json \
    | python $STAN_MODEL/aggregate-data.py \
    | python stan-encoder.py --record $STAN_MODEL/models.csv \
	     > $STAN_MODEL/data.json
