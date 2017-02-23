# -*- coding: utf-8 -*-

"""
Copyright 2016 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Björn Buchhold <buchhold@cs.uni-freiburg.de>
Patrick Brosi <brosi@informatik.uni-freiburg.de>
"""

import re
import sys
import math
import numpy as np
import random
from math import exp
from scipy.sparse import csr_matrix


class InvertedIndex:
    """ A simple inverted index, as explained in the lecture.
        >>> np.set_printoptions(formatter={"float": lambda x: ("%.3f" % x)})
    """

    def __init__(self):
        """ Create an empty inverted index. """

        self.inverted_lists = dict()
        self.document_lengths = []
        self.avg_doc_length = 0
        self.rss = 0
        self.iterations = 0
        # term document matrix
        self.td_matrix = None
        # maps a term to the row index of the document matrix
        self.term_matrix_indices = dict()

    def read_from_file(self, file_name, bm25_k=1.75, bm25_b=0.75):
        """
        Construct inverted index from given file. The format is one record per
        line.

        Documents are unique in postings lists.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> ii.inverted_lists['docum'][0][0]
        1
        >>> '%.3f' %  ii.inverted_lists['docum'][0][1]
        '0.000'
        >>> ii.inverted_lists['docum'][1][0]
        2
        >>> '%.3f' %  ii.inverted_lists['docum'][1][1]
        '0.000'
        >>> ii.inverted_lists['docum'][2][0]
        3
        >>> '%.3f' %  ii.inverted_lists['docum'][2][1]
        '0.000'
        >>> ii.inverted_lists['first'][0][0]
        1
        >>> '%.3f' %  ii.inverted_lists['first'][0][1]
        '1.885'
        >>> ii.inverted_lists['second'][0][0]
        2
        >>> '%.3f' %  ii.inverted_lists['second'][0][1]
        '2.325'
        >>> ii.inverted_lists['third'][0][0]
        3
        >>> '%.3f' %  ii.inverted_lists['third'][0][1]
        '2.521'
        """

        with open(file_name) as file:
            doc_id = 0
            for line in file:
                doc_id += 1
                self.document_lengths.append(0)
                for word in re.split("\W+", line):
                    word = word.lower()
                    if len(word) > 0:
                        self.document_lengths[-1] += 1
                        self.avg_doc_length += 1
                        """ If word seen for first time, create empty inverted
                        list for it. """
                        if word not in self.inverted_lists:
                            self.inverted_lists[word] = list()

                        """
                        A doc_id collision can only occur if the last
                        entry in the word's postings lists is the current
                        doc_id (postings list is implicitely sorted by the
                        increasing doc_id). """
                        if (len(self.inverted_lists[word]) == 0 or
                                self.inverted_lists[word][-1][0] != doc_id):
                            """ First occurence of this document for this word,
                            set term frequency (tf) to 1 """
                            self.inverted_lists[word].append((doc_id, 1))
                        elif self.inverted_lists[word][-1][0] == doc_id:
                            """ Document already stored for this word,
                                increment tf by 1 """
                            self.inverted_lists[word][-1] = \
                                (doc_id, self.inverted_lists[word][-1][1] + 1)

        """ (N == doc_id) """
        self.avg_doc_length = self.avg_doc_length / doc_id

        self.transform_to_bm25(bm25_k, bm25_b)

    def preprocess_vsm(self, l2normalize=False):
        """
        Exercise 08.01
        Construct the sparse term-document matrix.

        >>> ii = InvertedIndex() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> ii.inverted_lists = {"bla": [(1, 0.2), (3, 0.6)],
        ... "blubb": [(2, 0.4), (3, 0.1), (4, 0.8)]}
        >>> ii.preprocess_vsm()
        >>> print(np.round(sorted(ii.td_matrix.todense().tolist()), 3))
        [[0.000 0.400 0.100 0.800]
         [0.200 0.000 0.600 0.000]]
        >>> ii.inverted_lists = {"blibb": [(1, 0.2), (2, 0.2), (3, 0.6)],
        ... "blabb": [(2, 0.4), (3, 0.1), (4, 0.8)]}
        >>> ii.preprocess_vsm(True)
        >>> l = sorted(ii.td_matrix.todense().tolist())
        >>> print(np.round(l, 3))
        [[0.000 0.894 0.164 1.000]
         [1.000 0.447 0.986 0.000]]
        """

        rows = []
        cols = []
        vals = []
        for i, term in enumerate(self.inverted_lists):
            self.term_matrix_indices[term] = i
            for docId, score in self.inverted_lists[term]:
                # row i is the term's row
                rows.append(i)
                # col docId is the documents column
                cols.append(docId - 1)
                # the entries of the term-doc matrix are the BM25 scores
                vals.append(score)

        # use float values because of BM25 scores
        self.td_matrix = csr_matrix((vals, (rows, cols)), dtype=float)

        # L^2-normalize
        if l2normalize:
            self.td_matrix = self.l2normalize_cols(self.td_matrix)

    def l2normalize_cols(self, matrix):
        """
        Functions to L2-normalize the columns of the given matrix.

        >>> ii = InvertedIndex()
        >>> m = csr_matrix([[ 0.7, 0.4, 0.1], \
            [ 1.9, 0.5, 2.9]])
        >>> ii.l2normalize_cols(m).todense()
        matrix([[0.346, 0.625, 0.034],
                [0.938, 0.781, 0.999]])
        """
        # square values
        squared = matrix.multiply(matrix)
        # sum squares and take squareroot
        a = np.sqrt(squared.sum(0))
        # divide each column by the the L^2 norm
        return matrix.multiply(csr_matrix(1/a))

    def transform_to_bm25(self, k=1.75, b=0.75):
        """
        Exercise 02.01
        Transform term frequencies to BM25 scores
        """

        for word, il in self.inverted_lists.items():
            idf = math.log(len(self.document_lengths) / len(il), 2)
            for i, docs in enumerate(il):
                denom = (k * (1 - b + b *
                              (self.document_lengths[docs[0]-1] /
                               self.avg_doc_length)) + docs[1])
                tf = docs[1]
                tf_star = tf * (k + 1) / denom
                il[i] = (docs[0], tf_star * idf)
                # il[i] = (docs[0], tf * idf)

    def initialize_centroids(self, k):
        self.centroids = np.zeros([k, len(self.inverted_lists)])
        centroids_indices = random.sample(
                                range(0, len(self.document_lengths)), k)
        for i, index in enumerate(centroids_indices):
            self.centroids[i] = np.array(self.td_matrix.toarray()[:, index])
        self.centroids = csr_matrix(self.centroids.T)

    def compute_distances(self):
        self.centroids = self.l2normalize_cols(self.centroids)
        self.distances = csr_matrix(1 - np.dot(
                    self.centroids.T.todense(), self.td_matrix.todense()))
        self.rss = np.sum(self.distances.toarray())

    def compute_assignment(self):
        rows = np.argmin(self.distances.todense(), axis=0).tolist()[0]
        cols = list(range(self.distances.shape[1]))
        values = [1] * self.distances.shape[1]
        self.distances = csr_matrix((values, (
                            rows, cols)), shape=self.distances.shape).todense()

    def compute_centroids(self, k):
        self.centroids = csr_matrix(np.dot(self.td_matrix.todense(),
                                    self.distances.T) /
                                    self.distances.sum(1).reshape(k,))

    def kmeans(self, k):
        self.initialize_centroids(k)
        oldRss = 10000
        while oldRss - self.rss > exp(10e-3):
            oldRss = self.rss
            self.compute_distances()
            self.compute_assignment()
            self.compute_centroids(k)
            self.iterations += 1

        print(self.iterations)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python3 inverted_index.py <file>")
        sys.exit()
    file_name = sys.argv[1]
    ii = InvertedIndex()
    ii.read_from_file(file_name)
    print("Building sparse term-document matrix...")
    ii.preprocess_vsm(True)
    print(ii.td_matrix.todense())
    print("Done.")
    ii.kmeans(2)
    print(ii.centroids.todense())
