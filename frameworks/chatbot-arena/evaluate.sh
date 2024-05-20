#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

_configs=$ROOT/alpaca_eval/src/alpaca_eval/models_configs
while getopts 'm:e:p:' option; do
    case $option in
	m) _model=$OPTARG ;;
	e) _encodings=$OPTARG ;;
	p) _parameters=( ${_parameters[@]} --parameter $OPTARG ) ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

tmp=`mktemp`

python $ROOT/utils/aggregate-output.py --results $_model/output \
    | python $ROOT/utils/unencode-results.py ${_parameters[@]} \
	     --encodings $_encodings

rm $tmp
