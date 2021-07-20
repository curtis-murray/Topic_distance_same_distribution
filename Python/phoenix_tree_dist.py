import pandas as pd
import numpy as np
import os
import timeit
import cProfile
import re
import time
import sys
import glob
import math

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
#TODO: would be good to log p first
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
full_data = pd.read_csv("data/Tidy_Topics/sample_0.csv")[["word_ID_full","topic","p"]].set_index('word_ID_full').T.to_dict('list')

# Get sample data
sample_data = pd.read_csv("data/Tidy_Topics/sample_"+str(sample)+".csv")[["word_ID_full","topic","p"]].set_index('word_ID_full').T.to_dict('list')

def total_dist(full_data,  sample_data):
    total_d = [0,0,0,0,0]
    max_depth_full = len(list(full_data.items())[1][1][0].split("-"))
    max_depth_sample = len(list(sample_data.items())[1][1][0].split("-"))
    # Nested through upper triangle of adjacency matrix computing weighted
    # path length on each itteration
    for i in range(1,n_words+1):
        for j in range(i+1,n_words+1):
            #print(str(i) + " " + str(j))
            part_d = weighted_diff_path_length(i,j, full_data, sample_data, max_depth_full, max_depth_sample)
            total_d = [total_d[x] + part_d[x] for x in range(len(total_d))]
    return total_d

def weighted_diff_path_length(i,j, full_data,  sample_data,  max_depth_full, max_depth_sample):
    # Computed the weighted difference in path lenghts
    # weighted by p_word(i) and p_word(j)
    d = [0,0,0,0,0]
    # Find path lengths
    d_full_ = joint_prob_given_LCA(i,j, full_data, max_depth_full)
    d_full = d_full_.get('depth')
    log_p_full = d_full_.get('log_p')
    d_samp_ = joint_prob_given_LCA(i,j, sample_data,  max_depth_sample)
    d_samp = d_samp_.get('depth')
    log_p_samp = d_samp_.get('log_p')
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
    # Joint prob of word | LCA
    d[4] = abs(math.exp(log_p_full)-math.exp(log_p_samp))
    return d

def path_length(i,j,data, max_depth):
    # DEPRECATED
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

# TODO: THIS NEEDS A BETTER NAME AS IT ALSO FINDS THE MAX DEPTH
def joint_prob_given_LCA(i,j,data, max_depth):
    # Funciton to compute path lengths between distinct words
    topic_i = data.get(i)
    topic_j = data.get(j)
    # If either or both words are not part of the data return the max path length (2*depth)
    if (topic_i is None) | (topic_j is None):
        # Return p = 0 and log(0) = -math.inf
        return {"depth": max_depth*2,"log_p": -math.inf}
    # If the words are the same then the path length is 0
    # Never true as only take upper triangle
    if i == j:
        return {"depth": 0,"log_p": math.log(1)}
    topic_i_id = topic_i[0].split("-")
    topic_i_p = topic_i[1].split("_")
    topic_j_id = topic_j[0].split("-")
    topic_j_p = topic_i[1].split("_")

    # import string and look for substrings and stuff
    # Loop through hierarchy, starting at deepest level
    # If words are in same topic return distance (starting at 2)
    # Othewise move up hierarcy and add 2 to path length
    for depth in range(max_depth):
        if topic_i_id[depth] == topic_j_id[depth]:
            LCA = depth+1
            break
    log_p = 0
    for depth in range(LCA):
        log_p = log_p + math.log(float(topic_i_p[depth])) + math.log(float(topic_j_p[depth]))
    return {"depth": (LCA)*2,"log_p": log_p}

def display_results(i,j):
    full_topic_i = full_data.get(i)
    full_topic_j = full_data.get(j)

    samp_topic_i = sample_data.get(i)
    samp_topic_j = sample_data.get(j)

    max_depth_full = len(list(full_data.items())[1][1][0].split("-"))
    max_depth_sample = len(list(sample_data.items())[1][1][0].split("-"))

    full_joint = joint_prob_given_LCA(i,j,full_data, max_depth_full)
    samp_joint = joint_prob_given_LCA(i,j,sample_data,max_depth_sample)

    d = weighted_diff_path_length(i,j, full_data,  sample_data,  max_depth_full, max_depth_sample)

    print(
        "full_topic_i:\n" + str(full_topic_i) + "\n\n" +
        "full_topic_j:\n" + str(full_topic_j) + "\n\n" +
        "full_info:\n" + str(full_joint) + "\n\n" +
        "samp_topic_i:\n" + str(samp_topic_i) + "\n\n" +
        "samp_topic_j:\n" + str(samp_topic_j) + "\n\n" +
        "samp__info:\n" + str(samp_joint) + "\n\n" +
        "d:\n" + str(d)
    )



d = total_dist(full_data, sample_data)

print("Distance of " + str(d))

pd.DataFrame({"sample": [sample],
"distance_unweighted": [d[0]],
"distance_all_subs_weighted": [d[1]],
"distance_both_subs_weighted": [d[2]],
"distance_sub_weighted": [d[3]],
"distance_joint_prob_given_LCA": [d[4]]
}).to_csv("data/Tree_Distance/sample_"+str(sample)+".csv", index = False, header=False)
