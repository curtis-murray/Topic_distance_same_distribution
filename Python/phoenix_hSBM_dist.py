import matplotlib
import os
import pylab as plt
from sbmtm import sbmtm
from document_simulator import document_simulator
import graph_tool.all as gt
import pandas as pd
import numpy as np
import re
from itertools import chain
import sys
import glob
import time

# The sample id is passed in as an argument
sample = int(sys.argv[1])
data = pd.read_csv("data/clean_posts.csv")

if sample == 0:
    texts = data["Content"].values.tolist()
    titles = data["Post_ID"].values.tolist()
    texts = [c.split() for c in texts]
else:
    # Consult the sample_info dataframe to work out what proportion of the data we sample
    sample_info = pd.read_csv("data/Samples.info/samples.csv")
    sample_prop = sample_info.query("sample == @sample")['sample_prop'].iloc[0]
    #sample_prop = float(sample_prop) #This stops things from breaking? I don't understand why it's neccesary

    n_docs = data.shape[0]
    n_docs_sample = round(sample_prop*n_docs)
    #When we're not sampling from a proportion and just taking the number of docs
    n_docs_sample = sample_prop
    # Get texts and titles
    p_w_tw = np.load("data/Samples/p_w_tw0_0.npy")
    p_tw_td = np.load("data/Samples/p_tw_td0_0.npy")
    my_gen = document_simulator()
    my_gen.specify_model(p_w_tw = p_w_tw, p_tw_td = p_tw_td)
    my_gen.sim_docs(n_docs = n_docs_sample,n_words = 425)

    texts = my_gen.get_docs()
    titles = range(0,n_docs_sample)

if len(glob.glob("data/Samples/words_all_*"+str(sample)+".csv")) > 0:
    print("Already done " + str(sample))
    quit()

def run_hSBM(texts, titles, sample):
    # Function to run the hSBM given the data, sample props, and sample ID (now called sample)
    model = sbmtm()

    ## we have to create the word-document network from the corpus
    model.make_graph(texts,documents=titles)

    ## we can also skip the previous step by saving/loading a graph
    # model.save_graph(filename = 'graph.xml.gz')
    # model.load_graph(filename = 'graph.xml.gz')

    ## fit the model
    # Loop a few times to make sure we actually get something! (sometimes the number of topics may be 0)
    for i in range(10):
        time_start = time.time()
        model.fit()
        time_end = time.time()
        topics = model.topics(l=0,n=10)
        if len(topics) > 1:
            break
    print(model.L)
    # Write time taken to execute and mdl
    pd.DataFrame.to_csv(pd.DataFrame({"seconds": [time_end - time_start]}),"".join(["data/hSBM_time/",str(sample), ".csv"]))
    pd.DataFrame.to_csv(pd.DataFrame({"mdl": [model.mdl]}),"".join(["data/hSBM_mdl/",str(sample), ".csv"]))

    for level in range(0,model.L+1):

        group_results = model.get_groups(l = level)
        p_w_tw = group_results['p_w_tw']
        pd.DataFrame.to_csv(pd.DataFrame(p_w_tw), "".join(["data/Samples/p_w_tw", str(level),"_", str(sample), ".csv"]))

        if sample == 0:
            p_tw_td = group_results['p_tw_td']
            p_td_d = group_results['p_td_d']

            pd.DataFrame.to_csv(pd.DataFrame(p_tw_td), "".join(["data/Samples/p_tw_td", str(level),"_", str(sample), ".csv"]))
            pd.DataFrame.to_csv(pd.DataFrame(p_td_d), "".join(["data/Samples/p_td_d", str(level), "_", str(sample), ".csv"]))

            np.save("data/Samples/p_w_tw" + str(level) + "_" +  str(sample) + ".npy",p_w_tw)
            np.save("data/Samples/p_tw_td" + str(level) + "_" +  str(sample) + ".npy",p_tw_td)
            np.save("data/Samples/p_td_d" + str(level) + "_" +  str(sample) + ".npy",p_td_d)

    pd.DataFrame.to_csv(pd.DataFrame(model.words), "".join(["data/Samples/words_all_", str(sample),  ".csv"]))
    pd.DataFrame.to_csv(pd.DataFrame(model.documents), "".join(["data/Samples/docs_all_", str(sample),  ".csv"]))

# Run hSBM
while(1):
    try:
        print("Running hSBM on sample: " + str(sample))
        run_hSBM(texts, titles, sample)
        break
    except Exception as e:
        print(e)
        print("Something went wrong, trying again...")
