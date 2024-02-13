#!/bin/bash

export PYTHONPATH=.
export PYTHONLOGLEVEL=info

ALPACA_ROOT=$HOME/alpaca_eval

(cd $ALPACA_ROOT && git pull origin main) 1>&2
python compile-results.py --results $ALPACA_ROOT/results \
    | python prompt-encoder.py --record prompts.json \
    | python dedup-order.py \
    | python make-data.py \
    | python codify-models.py --record models.csv \
    | python to-stan.py
