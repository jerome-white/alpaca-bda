#!/bin/bash

ALPACA_ROOT=$HOME/Public/misc/alpaca_eval

python compile-results.py --results $ALPACA_ROOT/results \
    | python prompt-encoder.py --dump prompts.json \
    | python dedup-order.py
