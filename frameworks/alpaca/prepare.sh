#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

_baselines=(
    gpt4_1106_preview
)

while getopts 'e:' option; do
    case $option in
	e) _encodings=$OPTARG ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

baseline=`sed -e's/ / --baseline /g' <<< ${_baselines[@]}`

git submodule update --remote --merge 1>&2
python $ROOT/utils/compile-results.py --baseline $baseline \
       --results $ROOT/frameworks/alpaca/alpaca_eval/results \
    | python $ROOT/utils/encode-results.py --save-encodings $_encodings
