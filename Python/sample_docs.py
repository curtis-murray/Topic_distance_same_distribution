import pandas as pd
import numpy
import random

p_w_tw = numpy.load("data/Samples/p_w_tw0_0.npy")
p_tw_td = numpy.load("data/Samples/p_tw_td0_0.npy")

class document_simulator():
    '''
    Class for simulating documents from a network topic model
    '''
    #def __init__(self):
    # No init methods yet
    def specify_model(self, p_w_tw,p_tw_td):
        p_td = numpy.sum(p_tw_td,axis=0)
        p_td_cum = numpy.cumsum(p_td, axis=0)
        p_tw_td_norm = p_tw_td/p_td
        p_tw_td_cum = numpy.cumsum(p_tw_td_norm,axis = 0)
        p_w_tw_cum = numpy.cumsum(p_w_tw,axis = 0)

        self.p_td = p_td
        self.p_td_cum = p_td_cum
        self.p_tw_td_norm = p_tw_td_norm
        self.p_tw_td_cum = p_tw_td_cum
        self.p_w_tw_cum = p_w_tw_cum

        return self

    # Function to simulate n_docs with n_words each
    def sim_docs(self,n_docs,n_words):

        self.n_docs = n_docs
        self.n_words = n_words

        # Function to simulate a document topic
        def sim_doc_topic(self):
            return numpy.argmax(self.p_td_cum > random.random())
        # Function to simulate a word topic given a doc topic
        def sim_word_topic(self, doc_topic):
            return numpy.argmax(self.p_tw_td_cum[:,doc_topic] > random.random())
        # Function to simulate a word given a word topic
        def sim_word(self, word_topic):
            return numpy.argmax(self.p_w_tw_cum[:,word_topic] > random.random())
        # Function to simulate a document with n_words given a document topic
        def sim_doc(self,doc_topic):
            return [sim_word(self, word_topic = sim_word_topic(self, doc_topic = doc_topic)) for x in range(self.n_words)]

        docs = [sim_doc(self, doc_topic = sim_doc_topic(self)) for x in range(self.n_docs)]
        self.docs = docs
        return self

    def get_docs(self):
        docs = self.docs
        return docs

my_gen = document_simulator()
my_gen.specify_model(p_w_tw = p_w_tw, p_tw_td = p_tw_td)
my_gen.sim_docs(n_docs = 100000,n_words = 50)
my_gen.get_docs()