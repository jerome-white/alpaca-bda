#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

_configs=$ROOT/alpaca_eval/src/alpaca_eval/models_configs
while getopts 'm:e:o:p:' option; do
    case $option in
	m) _model=$OPTARG ;;
	e) _encodings=$OPTARG ;;
	o) _output=$OPTARG ;;
	p) _parameters=( ${_parameters[@]} --parameter $OPTARG ) ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

tmp=`mktemp`

python $ROOT/utils/pretty-names.py --configs $_configs < $_encodings > $tmp
python $ROOT/utils/aggregate-output.py --results $_model/output \
    | python $ROOT/utils/unencode-results.py ${_parameters[@]} \
	     --encodings $tmp \
    | gzip --to-stdout --best > $_output

rm $tmp
