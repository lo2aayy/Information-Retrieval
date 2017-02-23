"""
Copyright 2016 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
"""

import re
import sys
import numpy as np
import math


class InvertedIndex:
    """ A simple inverted index, as explained in Lecture 1. """

    def __init__(self):
        """ Create an empty inverted index. """

        self.inverted_lists = {}
        self.terms = []
        self.num_terms = 0
        self.num_docs = 0
        self.avdl = 0
        self.dl = []
        self.words = {}

    def read_from_file(self, file_name):
        """ Construct from given file (one record per line).

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> [ii.num_terms, ii.num_docs]
        [4, 3]
        >>> ii.terms
        ['first', 'doc', 'second', 'third']
        >>> sorted(ii.inverted_lists.items())
        [('doc', [1, 2, 3]), ('first', [1]), ('second', [2]), ('third', [3])]
        """

        doc_id = 0
        word_id = 0
        with open(file_name) as file:
            for line in file:
                doc_dl = 0
                doc_id += 1
                for term in re.split("\W+", line):
                    term = term.lower()
                    if len(term) > 0:
                        # If term seen first time, create inverted list.
                        if term not in self.inverted_lists:
                            self.terms.append(term)
                            self.inverted_lists[term] = []
                            self.words[term] = word_id
                            word_id += 1
                        # Append record id to inverted list.
                        self.inverted_lists[term].append(doc_id)
                        self.avdl += 1
                        doc_dl += 1
                self.dl.append(doc_dl)
        self.num_terms = len(self.inverted_lists.keys())
        self.num_docs = doc_id
        self.avdl //= doc_id

    def preprocess_vsm(self):
        """ Build the term-document matrix from the inverted index.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example2.txt")
        >>> ii.preprocess_vsm()
        array([[ 1.,  1.,  0.,  1.,  0.,  0.],
               [ 1.,  0.,  1.,  1.,  0.,  0.],
               [ 1.,  1.,  1.,  2.,  1.,  1.],
               [ 0.,  0.,  0.,  1.,  1.,  1.]])
        """
        A = np.zeros((self.num_terms, self.num_docs), dtype=float)
        for term_id, term in enumerate(self.terms):
            for doc_id in self.inverted_lists[term]:
                A[term_id, doc_id - 1] += 1
        return A

    def bm25(self, A, k, b):
        """ Calculates the bm25 scores and adds it inplace. """
        self.tfStar(A, k, b)
        self.idf(A)

    def tfStar(self, A, k, b):
        """ Replace tf values in the td matrix with td*. """
        for col in range(A.shape[1]):
            A[:, col] *= ((k + 1)/(k * (1 - b + b * self.dl[col] /
                                        self.avdl) + A[:, col]))

    def idf(self, A):
        """ Multiplies each value in the td matix with idf. """
        for row in range(A.shape[0]):
            A[row] *= math.log(self.num_docs / np.count_nonzero(A[row]), 2)

    def process_query_vsm(self, A, query):
        """ Returns the best matches for the query from the td matrix.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example2.txt")
        >>> A = ii.preprocess_vsm()
        >>> ii.bm25(A, 1.75, 0.75)
        >>> ii.process_query_vsm(A, "web surfing")
        array([[ 3.        ,  1.        ],
               [ 1.        ,  0.80733945],
               [ 4.        ,  0.58278146],
               [ 6.        ,  0.        ],
               [ 5.        ,  0.        ],
               [ 2.        ,  0.        ]])
        """
        q = np.zeros(len(self.words))
        docs = np.linspace(1, self.num_docs, num=self.num_docs)
        for term in re.split("\W+", query):
                    term = term.lower()
                    if self.words[term]:
                        q[self.words[term]] = 1

        results = np.column_stack((docs, q.dot(A)))
        return results[results[:, 1].argsort()[::-1]]

if __name__ == "__main__":
    """ Gets input query from the user and prints the results. """
    # Parse command line arguments.
    if len(sys.argv) != 2:
        print("Usage: python3 inverted_index.py <file>")
        sys.exit()
    file_name = sys.argv[1]
    # Output the lengths.
    ii = InvertedIndex()
    ii.read_from_file(file_name)
    A = ii.preprocess_vsm()
    ii.bm25(A, 1.75, 0.75)
    q = str(input('Search query: '))
    scores = ii.process_query_vsm(A, q)
    print("\nScores:")
    print(scores)
