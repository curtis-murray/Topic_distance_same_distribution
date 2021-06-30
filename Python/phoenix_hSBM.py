import matplotlib
import os
import pylab as plt
from sbmtm import sbmtm
import graph_tool.all as gt
import pandas as pd
import numpy as np
import re
from itertools import chain
import sys
import glob

# The sample id is passed in as an argument
sample = int(sys.argv[1])

# Consult the sample_info dataframe to work out what proportion of the data we sample
sample_info = pd.read_csv("data/Samples.info/samples.csv")
sample_prop = sample_info.query("sample == @sample")['sample_prop'].iloc[0]
sample_prop = float(sample_prop) #This stops things from breaking? I don't understand why it's neccesary

if len(glob.glob("data/Samples/words_all_*"+str(sample)+".csv")) > 0:
    print("Already done " + str(sample))
    quit()

# These folders should exist but create them if they don't
if not os.path.exists("data"):
    os.system("mkdir data")

if not os.path.exists("data/Samples"):
    os.system("mkdir data/Samples")

if not os.path.exists("data/Tidy_Topics"):
    os.system("mkdir data/Tidy_Topics")

if not os.path.exists("data/Tree_Distance"):
    os.system("mkdir data/Tree_Distance")

def run_hSBM(texts, titles, sample_prop, itr):
    # Function to run the hSBM given the data, sample props, and sample ID (now called itr)
    model = sbmtm()

    ## we have to create the word-document network from the corpus
    model.make_graph(texts,documents=titles)

    ## we can also skip the previous step by saving/loading a graph
    # model.save_graph(filename = 'graph.xml.gz')
    # model.load_graph(filename = 'graph.xml.gz')

    ## fit the model
    # Loop a few times to make sure we actually get something!
    for i in range(10):
        model.fit()
        topics = model.topics(l=0,n=10)
        if len(topics) > 1:
            break
    print(model.L)
    for level in range(1,model.L+1):

        group_results = model.get_groups(l = level)
        p_w_tw = group_results['p_w_tw']
        pd.DataFrame.to_csv(pd.DataFrame(p_w_tw), "".join(["data/Samples/p_w_tw", str(level),"_", str(sample_prop) , "_", str(itr), ".csv"]))

    pd.DataFrame.to_csv(pd.DataFrame(model.words), "".join(["data/Samples/words_all_", str(sample_prop) , "_", str(itr),  ".csv"]))

data = pd.read_csv("data/clean_posts.csv")

# Change the name - leaving old name in case anything breaks
itr = sample

# Sample documents from full data
sample_ind = np.random.permutation(len(data))[range(round(sample_prop*len(data)))]
sample_data = data.loc[sample_ind]

# Get texts and titles
texts = sample_data["Content"].values.tolist()
titles = sample_data["Post_ID"].values.tolist()
texts = [c.split() for c in texts]

# Run hSBM
while(1):
    try:
        print("Running hSBM on sample: " + str(itr) + " with sample_prop: " + str(sample_prop))
        run_hSBM(texts, titles, sample_prop, itr)
        break
    except Exception as e:
        print(e)
        print("Something went wrong, trying again...")


