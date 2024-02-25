#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

_src=$ROOT/models/bradley-terry
_codes=$_src/codes.json
while getopts 'pseh' option; do
    case $option in
	p) _prepare=1 ;;
	s) _sample=1 ;;
	e) _evaluate=1 ;;
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
	| python $_src/aggregate-data.py \
	| python $_src/stan-encoder.py > $_src/data.json
fi || exit 1

#
#
#
if [ $_sample ]; then
    $ROOT/bin/sample.sh -m $_src -s 12000
fi || exit 2

#
#
#
if [ $_evaluate ]; then
    output=$_src/results.csv.gz

    python $ROOT/utils/aggregate-output.py --results $_src/output \
	| python $ROOT/utils/unencode-results.py \
		 --encodings $_codes \
		 --parameter alpha:model \
	| gzip --to-stdout --best > $output

    python $ROOT/utils/push-to-hub.py \
	   --source $output \
	   --target jerome-white/alpaca-bt-stan
fi || exit 3
