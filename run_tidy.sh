#!/bin/bash -l
#SBATCH -p batch                                                # partition (this is the queue your job will be added to)			$
#SBATCH -N 1                                                    # number of nodes
#SBATCH -n 4
#SBATCH --time=0-01:00:00                                       # walltime allocation, which has the format (D-HH:MM:SS), here set to 1 hour
#SBATCH --mem=16GB                                              # memory required per node (here set to 4 GB)

# Notification configuration
#SBATCH --mail-type=END                                         # Send a notification email when the job is done (=END)
#SBATCH --mail-type=FAIL                                        # Send a notification email when the job fails (=FAIL)
#SBATCH --mail-user=curtis.murray@adelaide.edu.au               # Email to which notifications will be sent

module load R

R CMD BATCH R/phoenix_tidy.R
