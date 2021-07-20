#!/bin/bash

source n_samp

sleep 8h

for i in $(seq 1 $n_samp)
do
  	echo $(date -u) "Running hSBM on samp $i"
        sbatch hSBM.sh $i
done






