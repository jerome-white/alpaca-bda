#!/bin/bash

ROOT=`git rev-parse --show-toplevel`
STAN_MODEL=$ROOT/models/bradley-terry
N=2000

_output=$STAN_MODEL/output
_summary=$STAN_MODEL/summary.csv
_workers=`nproc`

mkdir $_output 2> /dev/null || rm --recursive --force $_output/*
rm --force $_summary

$STAN_MODEL/model \
    sample num_samples=$N num_chains=$_workers \
    data file=$STAN_MODEL/data.json \
    output file=$_output/o.csv \
    num_threads=$_workers
stansummary --csv_filename=$_summary $_output/*.csv
