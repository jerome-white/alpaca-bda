#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

_model=$ROOT/models/bradley-terry
while getopts 'f:pseuh' option; do
    case $option in
	f)
	    _fm=$OPTARG
	    case `basename $_ftype` in
		alpaca) ;;
		chatbot-arena)
		    _dataset=arena
		    ;;
		*)
		    exit 1
		    ;;
	    esac
	    ;;
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

if [ ! -d $_fm ]; then
    exit 1
fi

codes=$_fm/codes.json
output=$_fm/results.csv.gz

#
#
#
if [ $_prepare ]; then
    $_fm/prepare.sh -e $codes \
	| python $_model/aggregate-data.py \
	| python $_model/stan-encoder.py > $_model/data.json
fi || exit 1

#
#
#
if [ $_sample ]; then
    $ROOT/bin/sample.sh -m $_model -s 8000
fi || exit 2

#
#
#
if [ $_evaluate ]; then
    $_fm/evaluate.sh -m $_model -e $codes -p alpha:model \
	| gzip --to-stdout --best > $output
fi || exit 3

#
#
#
if [ $_upload ]; then
    zcat $output \
	| python $ROOT/utils/push-to-hub.py \
		 --target jerome-white/${_dataset}-bt-stan
fi || exit 4
