#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT/mylib
export PYTHONLOGLEVEL=info

_src=$ROOT/models/item-response
_llms=$_src/models.csv
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
    $ROOT/bin/prepare.sh \
	| python $_src/aggregate-data.py \
	| python $_src/stan-encoder.py --record $_llms > $_src/data.json
fi

#
#
#
if [ $_sample ]; then
    $ROOT/bin/sample.sh -m $_src
fi
