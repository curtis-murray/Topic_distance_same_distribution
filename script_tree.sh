#!/bin/bash -l
#SBATCH -p batch            	                                # partition (this is the queue your job will be added to) 
#SBATCH -N 5               	                                # number of nodes (no MPI, so we only use a single node)
#SBATCH -n 5             	                                # number of cores
#SBATCH --ntasks-per-node=1
#SBATCH --time=1-03:00:00    	                                # walltime allocation, which has the format (D-HH:MM:SS), here set to 1 hour
#SBATCH --mem=16GB         	                                # memory required per node (here set to 4 GB)

# Notification configuration 
#SBATCH --mail-type=END					    	# Send a notification email when the job is done (=END)
#SBATCH --mail-type=FAIL   					# Send a notification email when the job fails (=FAIL)
#SBATCH --mail-user=curtis.murray@adelaide.edu.au  		# Email to which notifications will be sent

module load Anaconda3/2020.07
module load R

conda activate gt

mpirun -np 1 ./my_program_tree_dist.sh

conda deactivate
