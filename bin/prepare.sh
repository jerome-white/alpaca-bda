#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

_alpaca_eval=alpaca_eval
_alpaca_git=$ROOT/$_alpaca_eval
_output=$ROOT/etc

mkdir --parents $_output

if [ -d $_alpaca_git ]; then
    (cd $_alpaca_git && git pull origin main) 1>&2
else
    git clone https://github.com/tatsu-lab/${_alpaca_eval}.git
fi

python $ROOT/utils/compile-results.py --results $_alpaca_git/results \
    | python $ROOT/utils/prompt-encoder.py --record $_output/prompts.json
