#!/bin/bash

ROOT=`git rev-parse --show-toplevel`
ARENA_DATA="https://drive.google.com/file/d/1Kpg6HD1QCrytCVT7FgRvZhY885TnmpEo/view?usp=sharing"

while getopts 'e:' option; do
    case $option in
	e) _encodings=$OPTARG ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

git submodule update --remote --merge 1>&2
python $ROOT/utils/compile-results.py ${_baseline[@]} \
       --results $ROOT/alpaca_eval/results \
    | python $ROOT/utils/encode-results.py --save-encodings $_encodings
