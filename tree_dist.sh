#!/bin/bash -l
#SBATCH -p batch                                                # partition (this is the queue your job will be added to)			$
#SBATCH -N 1                                                    # number of nodes
#SBATCH -n 1
#SBATCH --time=0-04:00:00                                       # walltime allocation, which has the format (D-HH:MM:SS), here set to 1 hour
#SBATCH --mem=4GB                                              # memory required per node (here set to 4 GB)

# Notification configuration
#SBATCH --mail-type=END                                         # Send a notification email when the job is done (=END)
#SBATCH --mail-type=FAIL                                        # Send a notification email when the job fails (=FAIL)
#SBATCH --mail-user=curtis.murray@adelaide.edu.au               # Email to which notifications will be sent

module load Anaconda3/2020.07

conda activate gt

python3.9 Python/phoenix_tree_dist.py $1

conda deactivate










