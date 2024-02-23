#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT
export PYTHONLOGLEVEL=info

_src=$ROOT/models/item-response
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

baselines=(
    text_davinci_003
    # gpt4_turbo
    gpt4_1106_preview
)
baseline=`sed -e's/ / --baseline /g' <<< ${baselines[@]}`

#
#
#
if [ $_prepare ]; then
    $ROOT/bin/prepare.sh -o $_src -e $_codes \
	| python $_src/aggregate-data.py --baseline $baseline \
	| python $_src/stan-encoder.py --record $_llms > $_src/data.json
fi || exit 1

#
#
#
if [ $_sample ]; then
    $ROOT/bin/sample.sh -m $_src -s 4000
fi || exit 2

#
#
#
if [ $_evaluate ]; then
    output=$_src/results.csv.gz
    params=(
	alpha:prompt
	beta:prompt
	theta:model
    )
    parameter=`sed -e's/ / --parameter /g' <<< ${params[@]}`

    python $ROOT/utils/aggregate-output.py --results $_src/output \
	| python $ROOT/utils/unencode-results.py ${parameter[@]} \
		 --encodings $_codes \
	| gzip --to-stdout --best > $output

    python $ROOT/utils/push-to-hub.py \
	   --source $output \
	   --target jerome-white/alpaca-ir-stan
fi || exit 3
