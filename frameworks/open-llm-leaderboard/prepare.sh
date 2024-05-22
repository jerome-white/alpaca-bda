#!/bin/bash

ROOT=`git rev-parse --show-toplevel`
S3_BUCKET=s3://jerome-huggingface-leadboard-results/2024-05-15-063801-UTC

while getopts 'e:' option; do
    case $option in
	e) _encodings=$OPTARG ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done

python $ROOT/frameworks/open-llm-leaderboard/compile-results.py \
       --data-root /media/hdd \
    | python $ROOT/utils/encode-results.py \
	     --save-encodings $_encodings \
	     --config `dirname $0`/encoding-config.json \
