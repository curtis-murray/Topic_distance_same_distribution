import pandas as pd
import numpy as np
import os
import timeit
import cProfile
import re
import time
import sys
import glob

if not os.path.exists("data/Tree_Distance"):
    os.system("mkdir data/Tree_Distance")

# INPUT number of samples
sample = int(sys.argv[1])

#os.system("touch data/Tree_Distance/running_sample_"+str(sample))
print("Tree distance on sample: " + str(sample))

if len(glob.glob("data/Tree_Distance/sample_"+str(sample)+".csv")) > 0:
    print("Already done " + str(sample))
    quit()

# Data loading
# Tidy topics
# Vocab
Vocab_full = pd.read_csv("data/Vocab/sample_0.csv")[['word_ID_full', 'freq']].set_index('word_ID_full').T.to_dict('list')
Vocab_samp = pd.read_csv("data/Vocab/sample_"+str(sample)+".csv")[['word_ID_full', 'freq']].set_index('word_ID_full').T.to_dict('list')

n_words = len(Vocab_full)

# Set key-values to 0 for keys not in Vocab_samp
keys_full = list(Vocab_full.keys())
keys_sample = list(Vocab_samp.keys())

diff_sample = set(keys_full)-set(keys_sample)

for key in diff_sample:
    Vocab_samp.update({key:[0]})

# Preprocessing data
# Filter to full data
full_data = pd.read_csv("data/Tidy_Topics/sample_0.csv")[["word_ID_full","topic"]].set_index('word_ID_full').T.to_dict('list')
# Get sample data
sample_data = pd.read_csv("data/Tidy_Topics/sample_"+str(sample)+".csv")[["word_ID_full","topic"]].set_index('word_ID_full').T.to_dict('list')

def total_dist(full_data, sample_data):
    total_d = [0,0,0,0]
    max_depth_full = len(list(full_data.items())[1][1][0].split("-"))
    max_depth_sample = len(list(sample_data.items())[1][1][0].split("-"))
    # Nested through upper triangle of adjacency matrix computing weighted
    # path length on each itteration
    for i in range(1,n_words+1):
        for j in range(i+1,n_words+1):
            part_d = weighted_diff_path_length(i,j, full_data, sample_data, max_depth_full, max_depth_sample)
            total_d = [total_d[x] + part_d[x] for x in range(0,4)]
    return total_d

def weighted_diff_path_length(i,j, full_data, sample_data, max_depth_full, max_depth_sample):
    # Computed the weighted difference in path lenghts
    # weighted by p_word(i) and p_word(j)
    d = [0,0,0,0]
    # Find path lengths
    d_full = path_length(i,j, full_data, max_depth_full)
    d_samp = path_length(i,j, sample_data, max_depth_sample)
    # Overall prob of words in corpora
    p_full_i = Vocab_full.get(i)[0]
    p_full_j = Vocab_full.get(j)[0]
    # Prop of words in sample corpus
    p_samp_i = Vocab_samp.get(j)[0]
    p_samp_j = Vocab_samp.get(j)[0]
    # Prob of words in merged sub corpus TODO: weight by total number of words?
    p_ave_i = (p_full_i + p_samp_i)/2
    p_ave_j = (p_full_j + p_samp_j)/2
    # Unweighted distance
    d[0] = abs(d_full-d_samp)
    # Corpora weighted distance
    d[1] = d[0]*p_full_i*p_full_j
    # Corpus weighted distance
    d[2] = d[0]*p_ave_i*p_ave_j
    # Full weighted distance
    d[3] = abs(d_full*p_full_i*p_full_j - d_samp*p_samp_i*p_samp_j)
    return d

def path_length(i,j,data, max_depth):
    # Funciton to compute path lengths between distinct words
    topic_i = data.get(i)
    topic_j = data.get(j)
    # If either or both words are not part of the data return the max path length (2*depth)
    if (topic_i is None) | (topic_j is None):
        return max_depth*2
    # If the words are the same then the path length is 0
    # Never true as only take upper triangle
    if i == j:
        return 0
    topic_i = topic_i[0].split("-")
    topic_j = topic_j[0].split("-")
    # import string and look for substrings and stuff
    # Loop through hierarchy, starting at deepest level
    # If words are in same topic return distance (starting at 2)
    # Othewise move up hierarcy and add 2 to path length
    for depth in range(max_depth):
        if topic_i[depth] == topic_j[depth]:
            return (depth+1)*2

d = total_dist(full_data, sample_data)

print("Distance of " + str(d))

pd.DataFrame({"sample": [sample],
"distance_unweighted": [d[0]],
"distance_unweighted": [d[0]],
"distance_all_subs_weighted": [d[1]],
"distance_both_subs_weighted": [d[2]],
"distance_sub_weighted": [d[3]]
}).to_csv("data/Tree_Distance/sample_"+str(sample)+".csv", index = False, header=False)
