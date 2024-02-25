#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

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

git submodule update --recursive
python $ROOT/utils/compile-results.py ${_baseline[@]} \
       --results $ROOT/alpaca_eval/results \
    | python $ROOT/utils/encode-results.py --save-encodings $_encodings
