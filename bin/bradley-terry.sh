#!/bin/bash

ROOT=`git rev-parse --show-toplevel`
SRC=$ROOT/models/bradley-terry

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

_codes=$SRC/codes.json
_output=$SRC/results.csv.gz

while getopts 'pseuh' option; do
    case $option in
	p) _prepare=1 ;;
	s) _sample=1 ;;
	e) _evaluate=1 ;;
	u) _upload=1 ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

#
#
#
if [ $_prepare ]; then
    $ROOT/bin/prepare.sh -e $_codes \
	| python $SRC/aggregate-data.py \
	| python $SRC/stan-encoder.py > $SRC/data.json
fi || exit 1

#
#
#
if [ $_sample ]; then
    $ROOT/bin/sample.sh -m $SRC -s 8000
fi || exit 2

#
#
#
if [ $_evaluate ]; then
    $ROOT/bin/evaluate.sh -m $SRC -e $_codes -o $_output -p alpha:model
fi || exit 3

#
#
#
if [ $_upload ]; then
    python $ROOT/utils/push-to-hub.py \
	   --source $_output \
	   --target jerome-white/alpaca-bt-stan
fi
