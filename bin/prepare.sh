#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

_alpaca_eval=alpaca_eval
_alpaca_git=$ROOT/$_alpaca_eval

while getopts 'b:e:' option; do
    case $option in
	b) _baseline=( ${_baseline[@]} --baseline $OPTARG ) ;;
	e) _encodings=$OPTARG ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

if [ -d $_alpaca_git ]; then
    (cd $_alpaca_git && git pull origin main) 1>&2
else
    git clone https://github.com/tatsu-lab/${_alpaca_eval}.git
fi
python $ROOT/utils/compile-results.py ${_baseline[@]} \
       --results $_alpaca_git/results \
    | python $ROOT/utils/encode-results.py --save-encodings $_encodings
