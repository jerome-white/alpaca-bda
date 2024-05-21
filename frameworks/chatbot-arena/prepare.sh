#!/bin/bash

ROOT=`git rev-parse --show-toplevel`
ARENA_DATA="https://storage.googleapis.com/arena_external_data/public"

while getopts 'e:' option; do
    case $option in
	e) _encodings=$OPTARG ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

python $ROOT/utils/compile-results.py --source $ARENA_DATA \
    | python $ROOT/utils/encode-results.py \
	     --config `dirname $0`/encoding-config.json \
	     --save-encodings $_encodings
