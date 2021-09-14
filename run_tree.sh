#!/bin/bash

source n_samp

for i in $(seq 1 $n_samp)
do
  	echo $(date -u) "Running tree dist on samp $i"
        sbatch tree_dist.sh $i 
done






