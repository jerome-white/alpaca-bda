#!/bin/bash

ROOT=`git rev-parse --show-toplevel`
STAN_MODEL=$ROOT/models/bradley-terry

_output=$STAN_MODEL/output
_summary=$STAN_MODEL/summary.csv
_samples=200000

num_chains=`nproc`
num_samples=$(bc -l <<< "$_samples / $num_chains" \
		  | cut --delimiter='.' --fields=1
	   )

mkdir $_output 2> /dev/null || rm --recursive --force $_output/*
rm --force $_summary

$STAN_MODEL/model \
    sample num_samples=$num_samples num_chains=$num_chains \
    data file=$STAN_MODEL/data.json \
    output file=$_output/o.csv \
    num_threads=$num_chains
stansummary --csv_filename=$_summary $_output/*.csv
