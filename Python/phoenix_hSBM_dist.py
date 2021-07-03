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

sample = 0

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

def run_hSBM(texts, titles, sample):
    # Function to run the hSBM given the data, sample props, and sample ID (now called sample)
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
    for level in range(0,model.L+1):

        group_results = model.get_groups(l = level)
        p_w_tw = group_results['p_w_tw']
        p_tw_td = group_results['p_tw_td']
        p_td_d = group_results['p_td_d']

        pd.DataFrame.to_csv(pd.DataFrame(p_w_tw), "".join(["data/Samples/p_w_tw", str(level),"_", str(sample), ".csv"]))
        pd.DataFrame.to_csv(pd.DataFrame(p_tw_td), "".join(["data/Samples/p_tw_td", str(level),"_", str(sample), ".csv"]))
        pd.DataFrame.to_csv(pd.DataFrame(p_td_d), "".join(["data/Samples/p_td_d", str(level), "_", str(sample), ".csv"]))

        np.save("data/Samples/p_w_tw" + str(level) + "_" +  str(sample) + ".npy",p_w_tw)
        np.save("data/Samples/p_tw_td" + str(level) + "_" +  str(sample) + ".npy",p_tw_td)
        np.save("data/Samples/p_td_d" + str(level) + "_" +  str(sample) + ".npy",p_td_d)

    pd.DataFrame.to_csv(pd.DataFrame(model.words), "".join(["data/Samples/words_all_", str(sample),  ".csv"]))
    pd.DataFrame.to_csv(pd.DataFrame(model.documents), "".join(["data/Samples/docs_all_", str(sample),  ".csv"]))

data = pd.read_csv("data/clean_posts.csv")

data = data[1:3000]

# Get texts and titles
texts = data["Content"].values.tolist()
titles = data["Post_ID"].values.tolist()
texts = [c.split() for c in texts]

# Run hSBM
while(1):
    try:
        print("Running hSBM on sample: " + str(sample))
        run_hSBM(texts, titles, sample)
        break
    except Exception as e:
        print(e)
        print("Something went wrong, trying again...")


