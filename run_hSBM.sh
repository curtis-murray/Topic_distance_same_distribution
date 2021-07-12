#!/bin/bash

source n_samp

for i in $(0 0)
do
  	echo $(date -u) "Running hSBM on samp $i"
        sbatch hSBM.sh $i
done






