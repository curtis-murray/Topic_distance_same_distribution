import pandas as pd
import numpy
import random

class document_simulator():
    '''
    Class for simulating documents from a network topic model:
    Algorithm:
        1. For each document in n_docs:
            a. Sample a document topic from empirical densitie of document topics p(document_topic).
            b. For each word in document of n_words:
                i. Sample word topic from p(topic_word | topic_document).
                ii. Sample word from p(word | word_topic).
            c. Store document as array of words.
        2. Store documents as array of documents

    Example usage:
        p_w_tw = numpy.load("data/Samples/p_w_tw0_0.npy")
        p_tw_td = numpy.load("data/Samples/p_tw_td0_0.npy")
        my_gen = document_simulator()
        my_gen.specify_model(p_w_tw = p_w_tw, p_tw_td = p_tw_td)
        my_gen.sim_docs(n_docs = 1000,n_words = 50)
        my_gen.get_docs()
    '''
    #def __init__(self):
    # No init methods yet
    def specify_model(self, p_w_tw,p_tw_td):
        '''
        Specify the parameters of the model:
        Input:
            p_w_tw: Matrix of probabilities p(word | topic_word) at the deepest layer of network topic model.
            p_tw_td: Matrix of probabilites p(topic_word | topic_document) at the deepest layer of the network topic model.
        Output:
            p_td: Empirical document topic density matrix p(topic_document)
            p_tw_td: Matirx of probabilities p(topic_word | topic_document)
            p_x_x_cum: Cumsum of p_x_x to used in sampling with uniform random number
        '''
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
        '''
        Method to simulate documents.
        Input:
            n_docs: number of documents to simulate.
            n_words: number of words in each document.
        '''
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
        '''
        Return the sampled documents.
        Output:
            docs: Array of documents as arrays of words
        '''
        docs = self.docs
        return docs