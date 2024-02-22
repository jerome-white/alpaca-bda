#!/bin/bash

_samples=2000
_workers=`nproc`
while getopts 'm:s:w:h' option; do
    case $option in
        m) _model=$OPTARG ;;
	s) _samples=$OPTARG ;;
	w) _workers=$OPTARG ;;
        *)
            echo -e Unrecognized option \"$option\"
            exit 1
            ;;
    esac
done
_output=$_model/output
_summary=$_model/summary.csv

mkdir $_output 2> /dev/null || rm --recursive --force $_output/*
rm --force $_summary

(cd $CMDSTAN && make $_model/model) || exit 1
$_model/model \
    sample num_samples=$_samples num_chains=$_workers \
    data file=$_model/data.json \
    output file=$_output/o.csv \
    num_threads=$_workers
stansummary --csv_filename=$_summary $_output/*.csv
